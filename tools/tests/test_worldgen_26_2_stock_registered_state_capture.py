"""Source-free, fail-closed stock-registered 26.2 constructor-state receipt tests."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_registered_state_capture as state  # noqa: E402


def row(seed: int, key: int, kind: str, path: str, name: str, value: str) -> str:
    return f"{state.PREFIX}{seed}|{key}|{kind}|{path}|{name}|{value}"


def fake_group(seed: int, key: int) -> list[str]:
    result = [
        row(seed,key,"I","parameters","firstOctave","-3"),
        row(seed,key,"L","parameters","amplitudes","2"),
        row(seed,key,"A","parameters","amplitudes_0","3ff0000000000000"),
        row(seed,key,"A","parameters","amplitudes_1","0000000000000000"),
        row(seed,key,"D","normal","valueFactor","3ff0000000000000"),
    ]
    for branch in ("first","second"):
        path="normal/"+branch
        result.extend([
            row(seed,key,"I",path,"firstOctave","-3"),
            row(seed,key,"D",path,"lowestFreqInputFactor","3ff0000000000000"),
            row(seed,key,"D",path,"lowestFreqValueFactor","3fe0000000000000"),
            row(seed,key,"L",path,"amplitudes","2"),
            row(seed,key,"A",path,"amplitudes_0","3ff0000000000000"),
            row(seed,key,"A",path,"amplitudes_1","0000000000000000"),
            row(seed,key,"L",path,"noiseLevels","2"),
        ])
        live=path+"/noiseLevels[0]"
        for axis in ("xo","yo","zo"):
            result.append(row(seed,key,"D",live,axis,"3fe0000000000000"))
        result.append(row(seed,key,"P",live,"permutation",
                          bytes(range(256)).hex()))
        result.append(row(seed,key,"Z",path+"/noiseLevels[1]","absent","0"))
    result.append(row(seed,key,"E","sample","complete","1"))
    return result


def fixture() -> list[str]:
    return [line for seed in range(5) for key in range(3)
            for line in fake_group(seed,key)]


class RegisteredStateReceiptTests(unittest.TestCase):
    def test_exact_15_seed_key_states_two_separate_perlins_and_bits(self):
        output="Minecraft bootstrap log\n"+"\n".join(fixture())+"\n"
        samples=state.parse(output)
        self.assertEqual(len(samples),15)
        self.assertEqual([s["world_seed_bits"] for s in samples[::3]],
                         list(state.stock.SEEDS))
        self.assertEqual([s["noise_key"] for s in samples[:3]],
                         list(state.stock.NOISE_KEYS))
        self.assertFalse(any("source_java" in s for s in samples))

    def test_mutated_order_counts_octal_state_and_missing_bits_fail_closed(self):
        base=fixture()
        changes = [
            base[:-1],
            base[1:],
            [base[1],base[0],*base[2:]],
            [base[0],base[0],*base[1:]],
            [*base,"extra"],
            [s.replace("|0|0|I|parameters|","|1|0|I|parameters|")
             if i==0 else s for i,s in enumerate(base)],
            [s.replace("3ff0000000000000","7ff8000000000001",1)
             if i==2 else s for i,s in enumerate(base)],
            [s.replace(bytes(range(256)).hex(),"00"*256,1)
             if i==18 else s for i,s in enumerate(base)],
            [s.replace("|L|parameters|amplitudes|2","|L|parameters|amplitudes|3")
             if i==1 else s for i,s in enumerate(base)],
        ]
        for bad in changes:
            with self.subTest(first=bad[:2],length=len(bad)):
                with self.assertRaises(state.RegisteredStateError):
                    state.parse("\n".join(bad))
        with self.assertRaises(state.RegisteredStateError):
            state.parse("\n".join(base)+"\n"+state.FAILURE+
                        "registered-parameters|java.lang.IllegalStateException|bad")

    def test_bad_cross_branch_state_and_malformed_failure_tags_rejected(self):
        source=fixture()
        for needle,replacement in (
            ("|normal/first|", "|normal/second|"),
            ("|normal/first/noiseLevels[0]|P|",
             "|normal/first/noiseLevels[0]|Z|"),
        ):
            modified=[s.replace(needle,replacement) if i<40 else s
                      for i,s in enumerate(source)]
            with self.assertRaises(state.RegisteredStateError):
                state.parse("\n".join(modified))
        for malformed in (
            state.FAILURE+"x|y",
            state.FAILURE+"x|y|z|extra",
            state.FAILURE+"x|y|z\n"+state.FAILURE+"x|y|z",
        ):
            with self.assertRaises(state.RegisteredStateError):
                state.parse(malformed)

    @unittest.skipUnless(shutil.which("javac"),"javac required for reflection-only probe")
    def test_new_and_existing_source_free_bridges_compile_without_game_classes(self):
        with tempfile.TemporaryDirectory() as temp:
            result=subprocess.run(
                ["javac","-encoding","UTF-8","-d",temp,
                 str(state.stock.JAVA_SOURCE),str(state.PROBE)],
                check=False,capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
