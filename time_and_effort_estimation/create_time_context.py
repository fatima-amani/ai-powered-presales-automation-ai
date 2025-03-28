import pandas as pd
from pathlib import Path

def create_rag_context(csv_paths, output_file):
    """
    Processes multiple CSV files and creates a consolidated text context for LLM
    
    Args:
        csv_paths (list): List of paths to CSV files
        output_file (str): Path to output text file with consolidated context
    """
    # Define expected columns based on your structure
    columns = [
        "Module", "Feature", "Subfeature", "Description", "Additional Info",
        "Development Days", "DevOps Days", "Testing Days",
        "Development Hours", "DevOps Hours", "Testing Hours"
    ]
    
    # Read and combine all CSV files
    dfs = []
    for path in csv_paths:
        # Read CSV while handling formatting errors
        df = pd.read_csv(path, 
                        header=0,
                        names=columns,  # Use predefined column names
                        skipinitialspace=True,
                        on_bad_lines='warn')
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Rest of the processing remains the same
    knowledge_chunks = []
    
    for _, row in combined_df.iterrows():
        chunk_lines = []
        module_hierarchy = []
        
        for level in ["Module", "Feature", "Subfeature"]:
            if pd.notna(row[level]):
                module_hierarchy.append(row[level])
        
        if module_hierarchy:
            chunk_lines.append("## " + " > ".join(module_hierarchy))
        
        # Add descriptions
        for field in ["Description", "Additional Info"]:
            if pd.notna(row[field]):
                chunk_lines.append(f"{field}: {row[field]}")
        
        # Add development metrics
        metrics = []
        for field in ['Development Days', 'DevOps Days', 'Testing Days',
                      'Development Hours', 'DevOps Hours', 'Testing Hours']:
            if pd.notna(row[field]):
                metrics.append(f"{field}: {row[field]}")
        
        if metrics:
            chunk_lines.append("Metrics: " + ", ".join(metrics))
        
        if chunk_lines:
            knowledge_chunks.append("\n".join(chunk_lines))
    
    consolidated_context = "\n\n".join(knowledge_chunks)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(consolidated_context)
    
    print(f"Consolidated context created with {len(knowledge_chunks)} chunks")
    return consolidated_context

# Example usage:
if __name__ == "__main__":
    csv_files = [
                 "C:/Users/Fatima/OneDrive/Desktop/AI-Powered Presales Automation/ai-model/time_and_effort_estimation/estimate_data/data1.csv", 
                 "C:/Users/Fatima/OneDrive/Desktop/AI-Powered Presales Automation/ai-model/time_and_effort_estimation/estimate_data/data2.csv",
                 "C:/Users/Fatima/OneDrive/Desktop/AI-Powered Presales Automation/ai-model/time_and_effort_estimation/estimate_data/data3.csv", 
                 "C:/Users/Fatima/OneDrive/Desktop/AI-Powered Presales Automation/ai-model/time_and_effort_estimation/estimate_data/data4.csv",
                 "C:/Users/Fatima/OneDrive/Desktop/AI-Powered Presales Automation/ai-model/time_and_effort_estimation/estimate_data/data5.csv",
                 "C:/Users/Fatima/OneDrive/Desktop/AI-Powered Presales Automation/ai-model/time_and_effort_estimation/estimate_data/data6.csv"
                ]
    output_path = "time_estimate_context.txt"
    context = create_rag_context(csv_files, output_path)