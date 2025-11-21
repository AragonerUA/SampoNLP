// src/lib.rs

use pyo3::prelude::*;
use std::collections::{HashMap, HashSet};

fn find_best_split(
    token: &String,
    token_chars: &Vec<char>,
    scores: &HashMap<String, f64>,
    one_char_whitelist: &HashSet<String>,
    is_affix: bool,
) -> f64 {
    let n = token_chars.len();
    let mut dp: Vec<f64> = vec![-1.0; n + 1];
    dp[0] = 0.0;

    for i in 1..=n {
        for j in 0..i {
            if dp[j] > -1.0 {
                let sub: String = token_chars[j..i].iter().collect();

                // Degeneracy check
                if sub.chars().count() == 1 && !one_char_whitelist.contains(&sub) {
                    continue;
                }

                if is_affix && j != 0 && i != n {
                    continue;
                }
                
                if let Some(sub_score) = scores.get(&sub) {
                    let current_score = dp[j] + sub_score;
                    if current_score > dp[i] {
                        dp[i] = current_score;
                    }
                }
            }
        }
    }
    dp[n]
}


#[pyfunction]
fn run_scoring_iteration(
    root_candidates: HashSet<String>,
    affix_candidates: HashSet<String>,
    scores: HashMap<String, f64>,
    one_char_whitelist: HashSet<String>,
) -> PyResult<HashMap<String, f64>> {
    let mut new_scores = HashMap::with_capacity(root_candidates.len() + affix_candidates.len());
    
    // --- Root processing ---
    for token in root_candidates.iter() {
        let token_chars: Vec<char> = token.chars().collect();
        let n = token_chars.len();
        if n == 0 { continue; }
        
        let best_explanation_power = find_best_split(token, &token_chars, &scores, &one_char_whitelist, false);
        
        let initial_score = 1.0 / n as f64;
        let self_score = *scores.get(token).unwrap_or(&0.0);

        if best_explanation_power < 0.0 || self_score >= best_explanation_power {
            new_scores.insert(token.clone(), self_score);
        } else {
            let new_score = initial_score / (1.0 + best_explanation_power);
            new_scores.insert(token.clone(), new_score);
        }
    }
    
    // --- Affixes processing ---
    for token in affix_candidates.iter() {
        let token_chars: Vec<char> = token.chars().collect();
        let n = token_chars.len();
        if n == 0 { continue; }
        
        // is_affix = true
        let best_explanation_power = find_best_split(token, &token_chars, &scores, &one_char_whitelist, true);

        let initial_score = 1.0 / n as f64;
        let self_score = *scores.get(token).unwrap_or(&0.0);

        if best_explanation_power < 0.0 || self_score >= best_explanation_power {
            new_scores.insert(token.clone(), self_score);
        } else {
            let new_score = initial_score / (1.0 + best_explanation_power);
            new_scores.insert(token.clone(), new_score);
        }
    }

    Ok(new_scores)
}

#[pymodule]
fn samponlp(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_scoring_iteration, m)?)?;
    Ok(())
}