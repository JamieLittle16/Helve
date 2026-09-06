use std::collections::{HashMap, hash_map::Entry};

use helve_types::{ChunkGeneration, ChunkPos, DimensionId};

use crate::{ResidentChunkAccessError, ResidentChunkHandle};

/// Minimal statically-dispatched identity required by the cold resident directory.
///
/// This trait is crate-private: it is not a plugin/service boundary and introduces no runtime
/// dispatch requirement. It exists only so the exact same sparse lifecycle machinery can own the
/// block-only R2C bootstrap chunk and the later coherent multi-component chunk state.
pub(crate) trait ResidentChunkIdentity {
    fn generation(&self) -> ChunkGeneration;
}

/// Internal fail-closed admission result from [`ResidentDirectory`].
pub(crate) enum ResidentAdmissionError<E> {
    AlreadyResident { handle: ResidentChunkHandle },
    GenerationExhausted,
    Build(E),
}

/// One sparse COLD/BOUNDARY resident-chunk directory with generation allocation.
///
/// The directory intentionally owns no world semantics. It performs lifecycle discovery and exact
/// handle validation, while callers keep direct resolved chunk borrows for HOT work. Admission probes
/// the map exactly once and consumes a generation only after the caller's constructor succeeds.
#[derive(Debug)]
pub(crate) struct ResidentDirectory<Chunk>
where
    Chunk: ResidentChunkIdentity,
{
    id: DimensionId,
    resident: HashMap<ChunkPos, Chunk>,
    next_generation: u64,
}

impl<Chunk> ResidentDirectory<Chunk>
where
    Chunk: ResidentChunkIdentity,
{
    pub(crate) fn with_capacity(
        id: DimensionId,
        chunk_capacity: usize,
    ) -> Self {
        Self {
            id,
            resident: HashMap::with_capacity(chunk_capacity),
            next_generation: 1,
        }
    }

    pub(crate) const fn id(&self) -> DimensionId {
        self.id
    }

    pub(crate) fn len(&self) -> usize {
        self.resident.len()
    }

    pub(crate) fn discover(&self, position: ChunkPos) -> Option<ResidentChunkHandle> {
        self.resident.get(&position).map(|chunk| ResidentChunkHandle {
            dimension: self.id,
            position,
            generation: chunk.generation(),
        })
    }

    /// Admits one chunk through exactly one sparse-directory probe.
    ///
    /// `build` runs only for a vacant position and receives the generation reserved for the new
    /// incarnation. The sequence advances only after `build` succeeds and the chunk is inserted.
    pub(crate) fn admit_with<E, Build>(
        &mut self,
        position: ChunkPos,
        build: Build,
    ) -> Result<ResidentChunkHandle, ResidentAdmissionError<E>>
    where
        Build: FnOnce(ChunkGeneration) -> Result<Chunk, E>,
    {
        match self.resident.entry(position) {
            Entry::Occupied(entry) => Err(ResidentAdmissionError::AlreadyResident {
                handle: ResidentChunkHandle {
                    dimension: self.id,
                    position,
                    generation: entry.get().generation(),
                },
            }),
            Entry::Vacant(entry) => {
                let next_generation = self
                    .next_generation
                    .checked_add(1)
                    .ok_or(ResidentAdmissionError::GenerationExhausted)?;
                let generation = ChunkGeneration(self.next_generation);
                let chunk = build(generation).map_err(ResidentAdmissionError::Build)?;
                debug_assert_eq!(chunk.generation(), generation);
                entry.insert(chunk);
                self.next_generation = next_generation;
                Ok(ResidentChunkHandle {
                    dimension: self.id,
                    position,
                    generation,
                })
            }
        }
    }

    pub(crate) fn resolve(
        &self,
        handle: ResidentChunkHandle,
    ) -> Result<&Chunk, ResidentChunkAccessError> {
        self.validate_dimension(handle)?;
        let chunk = self
            .resident
            .get(&handle.position)
            .ok_or(ResidentChunkAccessError::NotResident {
                position: handle.position,
            })?;
        validate_generation(handle, chunk.generation())?;
        Ok(chunk)
    }

    pub(crate) fn resolve_mut(
        &mut self,
        handle: ResidentChunkHandle,
    ) -> Result<&mut Chunk, ResidentChunkAccessError> {
        self.validate_dimension(handle)?;
        let chunk = self
            .resident
            .get_mut(&handle.position)
            .ok_or(ResidentChunkAccessError::NotResident {
                position: handle.position,
            })?;
        validate_generation(handle, chunk.generation())?;
        Ok(chunk)
    }

    pub(crate) fn unload(
        &mut self,
        handle: ResidentChunkHandle,
    ) -> Result<Chunk, ResidentChunkAccessError> {
        self.validate_dimension(handle)?;
        match self.resident.entry(handle.position) {
            Entry::Vacant(_) => Err(ResidentChunkAccessError::NotResident {
                position: handle.position,
            }),
            Entry::Occupied(entry) => {
                validate_generation(handle, entry.get().generation())?;
                Ok(entry.remove())
            }
        }
    }

    fn validate_dimension(
        &self,
        handle: ResidentChunkHandle,
    ) -> Result<(), ResidentChunkAccessError> {
        if handle.dimension == self.id {
            Ok(())
        } else {
            Err(ResidentChunkAccessError::WrongDimension {
                expected: self.id,
                actual: handle.dimension,
            })
        }
    }
}

fn validate_generation(
    handle: ResidentChunkHandle,
    current: ChunkGeneration,
) -> Result<(), ResidentChunkAccessError> {
    if handle.generation == current {
        Ok(())
    } else {
        Err(ResidentChunkAccessError::StaleGeneration {
            position: handle.position,
            current,
            handle: handle.generation,
        })
    }
}
