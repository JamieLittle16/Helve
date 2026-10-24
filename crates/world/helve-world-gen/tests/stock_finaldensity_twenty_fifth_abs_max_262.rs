//! Original 26.2 nineteenth LEFT MAX of two actual 25th Mapped(ABS) inputs.
//! All 128 nodes feed genuinely newly captured *`IntervalSelect`* inputs into
//! unchanged native `CandidateAbs` twice, then `ExplicitAp2Max`. Older 24th
//! Mapped and 19th MAX parent outputs remain independent frozen expectations.
//! This is bounded finite evidence, not complete IntervalSelect/lifecycle.

use helve_world_gen::density_primitives_262::DensityPrimitive262 as Primitive;
use helve_world_gen::stock_density_program_262::{
    StockDensityNode262 as Node, StockDensityProgram262 as Program,
};

const NEW_INTERVAL: &str =
    include_str!("data/stock_finaldensity_twenty_fifth_two_interval_inputs_128_rawbits.tsv");
const PRIOR_MAPPED: &str =
    include_str!("data/stock_finaldensity_twenty_fourth_left_max_mapped_children_128_rawbits.tsv");
const PRIOR_NINETEENTH: &str =
    include_str!("data/stock_finaldensity_nineteenth_clamp_ap2_add_children_128_rawbits.tsv");

fn parse_ieee(word: &str) -> u64 {
    assert_eq!(word.len(), 16, "real original IEEE length changed");
    assert!(
        word.bytes()
            .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
    );
    let value = u64::from_str_radix(word, 16).expect("real original numeric word");
    assert!(f64::from_bits(value).is_finite());
    value
}

fn pair_words(line: &str) -> [u64; 2] {
    let (first, second) = line
        .split_once('\t')
        .expect("exact 2-column original fixture");
    assert!(!second.contains('\t'));
    [parse_ieee(first), parse_ieee(second)]
}

fn original_bounded_abs_max(input: [u64; 2]) -> ([u64; 2], u64) {
    let program = Program::new([
        Node::Primitive(Primitive::constant(f64::from_bits(input[0]))),
        Node::Primitive(Primitive::constant(f64::from_bits(input[1]))),
        Node::CandidateAbs { input: 0 },
        Node::CandidateAbs { input: 1 },
        Node::ExplicitAp2Max { left: 2, right: 3 },
    ])
    .expect("five-node original-only ABS+MAX finite candidate");
    let [a, b] = input;
    let left = (f64::from_bits(a)).abs().to_bits();
    let right = (f64::from_bits(b)).abs().to_bits();
    ([left, right], program.sample_block(0, 0, 0).to_bits())
}

#[test]
fn genuine_twenty_fifth_two_abs_interval_children_to_old_24th_and_19th_128() {
    let current: Vec<_> = NEW_INTERVAL.lines().collect();
    let mapped: Vec<_> = PRIOR_MAPPED.lines().collect();
    let root: Vec<_> = PRIOR_NINETEENTH.lines().collect();
    assert_eq!((current.len(), mapped.len(), root.len()), (128, 128, 128));
    let mut first_negative = 0;
    let mut second_negative = 0;
    let mut left_wins = 0;
    let mut right_wins = 0;
    for (i, line) in current.iter().enumerate() {
        let input = pair_words(line);
        let old_mapped = pair_words(mapped[i]);
        let old_root_left = pair_words(root[i])[0];
        first_negative += usize::from((input[0] >> 63) != 0);
        second_negative += usize::from((input[1] >> 63) != 0);
        let (mapped_output, actual) = original_bounded_abs_max(input);
        assert_eq!(mapped_output, old_mapped, "25th original ABS pair row {i}");
        assert_eq!(
            actual, old_root_left,
            "25th ABS pair -> original 19th MAX row {i}"
        );
        left_wins += usize::from(mapped_output[0] > mapped_output[1]);
        right_wins += usize::from(mapped_output[0] < mapped_output[1]);
    }
    assert_eq!((first_negative, second_negative), (65, 66));
    assert_eq!((left_wins, right_wins), (53, 75));
}
