//! Original 26.2 24th layer: actual nineteenth LEFT `MAX(Mapped, Mapped)`.
//! Two new original child IEEE words per 128 source-owned points, never
//! duplicating the nineteenth original LEFT parent values. Bounded numeric
//! sample proof, not generic mapped-law, lifecycle or production permission.

use helve_world_gen::density_primitives_262::DensityPrimitive262 as Primitive;
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program,
};

const ACTUAL_24TH_NEW_ONLY: &str =
    include_str!("data/stock_finaldensity_twenty_fourth_left_max_mapped_children_128_rawbits.tsv");
const ORIGINAL_19TH: &str =
    include_str!("data/stock_finaldensity_nineteenth_clamp_ap2_add_children_128_rawbits.tsv");

fn word(raw: &str) -> u64 {
    assert_eq!(raw.len(), 16, "original source IEEE64 word truncated");
    assert!(
        raw.bytes()
            .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
    );
    let bits = u64::from_str_radix(raw, 16).expect("source-owned original IEEE word");
    assert!(
        f64::from_bits(bits).is_finite(),
        "nonfinite original density"
    );
    bits
}

fn max_stage(left: u64, right: u64) -> Program<'static, 3> {
    Program::new([
        Node::Primitive(Primitive::constant(f64::from_bits(left))),
        Node::Primitive(Primitive::constant(f64::from_bits(right))),
        Node::ExplicitAp2Max { left: 0, right: 1 },
    ])
    .expect("original 24th cold-only three-node MAX candidate")
}

#[test]
fn actual_nineteenth_left_max_from_two_new_original_mapped_values_128() {
    let new: Vec<_> = ACTUAL_24TH_NEW_ONLY.lines().collect();
    let old: Vec<_> = ORIGINAL_19TH.lines().collect();
    assert_eq!((new.len(), old.len()), (128, 128));
    let mut a_wins = 0;
    let mut b_wins = 0;
    for (i, (row, parent)) in new.into_iter().zip(old).enumerate() {
        let child: Vec<_> = row.split('\t').collect();
        let original: Vec<_> = parent.split('\t').collect();
        assert_eq!((child.len(), original.len()), (2, 2));
        let a = word(child[0]);
        let b = word(child[1]);
        let old_left_parent = word(original[0]);
        let first = f64::from_bits(a);
        let second = f64::from_bits(b);
        assert_ne!(a, b, "real original 24th operands never tie at {i}");
        a_wins += usize::from(first > second);
        b_wins += usize::from(first < second);
        let actual = max_stage(a, b).sample_block(0, 0, 0).to_bits();
        assert_eq!(
            actual, old_left_parent,
            "original 24th MAX two Mapped children -> sealed 19th left parent row {i}"
        );
    }
    assert_eq!((a_wins, b_wins), (53, 75));
}
