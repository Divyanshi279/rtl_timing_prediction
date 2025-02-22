import os
import re
import networkx as nx
import pandas as pd

class RTLParser:
    def __init__(self, rtl_dir):
        self.rtl_dir = rtl_dir
        self.modules = {}
        self.graph = nx.DiGraph()
    
    def parse_verilog(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        module_name = None
        for line in lines:
            line = line.strip()
            if line.startswith('module'):
                module_name = re.findall(r'module\s+(\w+)', line)[0]
                self.modules[module_name] = []
            elif 'assign' in line or ('input' in line or 'output' in line):
                if module_name:
                    self.modules[module_name].append(line)
    
    def build_graph(self):
        for module, connections in self.modules.items():
            for conn in connections:
                signals = re.findall(r'\b\w+\b', conn)
                if len(signals) > 1:
                    for i in range(1, len(signals)):
                        self.graph.add_edge(signals[i], signals[0])
    
    def extract_features(self):
        features = []
        for node in self.graph.nodes:
            features.append({
                'signal': node,
                'fan_in': self.graph.in_degree(node),
                'fan_out': self.graph.out_degree(node),
                'logic_depth': nx.shortest_path_length(self.graph, source=node) if nx.has_path(self.graph, node, node) else 0
            })
        return features
    
    def run(self):
        for filename in os.listdir(self.rtl_dir):
            if filename.endswith('.v'):
                self.parse_verilog(os.path.join(self.rtl_dir, filename))
        self.build_graph()
        return self.extract_features()

# Run the parser and save dataset
parser = RTLParser('rtl_samples')
features = parser.run()

# Save as CSV
df = pd.DataFrame(features)
df.to_csv("rtl_dataset.csv", index=False)
print("Dataset saved as rtl_dataset.csv")
