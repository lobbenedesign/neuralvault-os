use pyo3::prelude::*;
use rand::prelude::*;
use rand_distr::{Normal, Distribution};
use rayon::prelude::*;
use std::collections::HashMap;

#[derive(Clone)]
pub struct RustCausalEdge {
    pub target_id: String,
    pub weight: f32,
}

#[derive(Clone)]
pub struct RustCausalNode {
    pub id: String,
    pub edges: Vec<RustCausalEdge>,
}

#[pyfunction]
pub fn run_stochastic_simulation_rs(
    start_node_id: String,
    initial_impact: f32,
    nodes_data: HashMap<String, Vec<(String, f32)>>,
    iterations: usize,
    depth: usize,
    noise_level: f32
) -> PyResult<HashMap<String, (f32, f32, f32)>> {
    // 1. Preparazione Grafo Rust
    let graph: HashMap<String, Vec<RustCausalEdge>> = nodes_data
        .into_iter()
        .map(|(id, edges)| {
            (
                id,
                edges
                    .into_iter()
                    .map(|(target, weight)| RustCausalEdge { target_id: target, weight })
                    .collect(),
            )
        })
        .collect();

    // 2. Esecuzione Parallela Monte Carlo (Rayon)
    let results: Vec<HashMap<String, f32>> = (0..iterations)
        .into_par_iter()
        .map(|_| {
            let mut rng = thread_rng();
            let normal = Normal::new(0.0, noise_level).unwrap();
            let mut current_impacts = HashMap::new();
            current_impacts.insert(start_node_id.clone(), initial_impact);

            let mut active_nodes = vec![(start_node_id.clone(), initial_impact)];

            for _ in 0..depth {
                let mut next_nodes = Vec::new();
                for (nid, impact) in active_nodes {
                    if let Some(edges) = graph.get(&nid) {
                        for edge in edges {
                            let noise = normal.sample(&mut rng);
                            let weight_with_noise = (edge.weight + noise).clamp(-2.0, 2.0);
                            let transmission = impact * weight_with_noise;
                            
                            let entry = current_impacts.entry(edge.target_id.clone()).or_insert(0.0);
                            *entry += transmission;
                            next_nodes.push((edge.target_id.clone(), transmission));
                        }
                    }
                }
                active_nodes = next_nodes;
                if active_nodes.is_empty() { break; }
            }
            current_impacts
        })
        .collect();

    // 3. Aggregazione Statistica
    let mut stats: HashMap<String, (Vec<f32>, f32)> = HashMap::new();
    for iter_res in results {
        for (id, val) in iter_res {
            stats.entry(id).or_insert((Vec::new(), 0.0)).0.push(val);
        }
    }

    let mut final_stats = HashMap::new();
    for (id, (vals, _)) in stats {
        let count = vals.len() as f32;
        let mean: f32 = vals.iter().sum::<f32>() / count;
        let variance: f32 = vals.iter().map(|v| (v - mean).powi(2)).sum::<f32>() / count;
        let std = variance.sqrt();
        let prob_pos = vals.iter().filter(|&&v| v > 0.0).count() as f32 / count;
        
        final_stats.insert(id, (mean, std, prob_pos));
    }

    Ok(final_stats)
}
