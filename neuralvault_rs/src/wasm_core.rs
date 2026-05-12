use wasm_bindgen::prelude::*;
use rand::prelude::*;
use rand_distr::{Normal, Distribution};
use std::collections::HashMap;

#[wasm_bindgen]
pub struct CausalEngineWasm {
    graph: HashMap<String, Vec<(String, f32)>>,
}

#[wasm_bindgen]
impl CausalEngineWasm {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self { graph: HashMap::new() }
    }

    pub fn set_graph(&mut self, data: JsValue) {
        let nodes: HashMap<String, Vec<(String, f32)>> = serde_wasm_bindgen::from_value(data).unwrap();
        self.graph = nodes;
    }

    pub fn simulate(&self, start_node: String, initial_impact: f32, iterations: usize, depth: usize, noise: f32) -> JsValue {
        let mut final_results: HashMap<String, Vec<f32>> = HashMap::new();
        let normal = Normal::new(0.0, noise).unwrap();

        for _ in 0..iterations {
            let mut rng = thread_rng();
            let mut impacts = HashMap::new();
            impacts.insert(start_node.clone(), initial_impact);

            let mut active = vec![(start_node.clone(), initial_impact)];

            for _ in 0..depth {
                let mut next = Vec::new();
                for (nid, impact) in active {
                    if let Some(edges) = self.graph.get(&nid) {
                        for (target, weight) in edges {
                            let w_noise = weight + normal.sample(&mut rng);
                            let trans = impact * w_noise;
                            *impacts.entry(target.clone()).or_insert(0.0) += trans;
                            next.push((target.clone(), trans));
                        }
                    }
                }
                active = next;
                if active.is_empty() { break; }
            }

            for (id, val) in impacts {
                final_results.entry(id).or_insert(Vec::new()).push(val);
            }
        }

        // Aggregate
        let mut stats = HashMap::new();
        for (id, vals) in final_results {
            let count = vals.len() as f32;
            let mean: f32 = vals.iter().sum::<f32>() / count;
            let prob_pos = vals.iter().filter(|&&v| v > 0.0).count() as f32 / count;
            stats.insert(id, (mean, prob_pos));
        }

        serde_wasm_bindgen::to_value(&stats).unwrap()
    }
}
