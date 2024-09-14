import spacy
import yaml
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from pathlib import Path
from collections import Counter
import logging
from WAAnalysis.config import DATA_DIR

# -------------------------------
# Setup Logging
# -------------------------------
log = logging.getLogger(__name__)

# -------------------------------
# Load NLP models
# -------------------------------
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer('all-MiniLM-L6-v2')

# -------------------------------
# Load Tags from YAML
# -------------------------------
def load_tags(yaml_file):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('tags', [])

# -------------------------------
# Generate Embeddings for Tags
# -------------------------------
def generate_embeddings(tags):
    """Generate sentence embeddings for each tag."""
    log.info(f"Generating embeddings for {len(tags)} tags.")
    embeddings = model.encode(tags)
    return embeddings

# -------------------------------
# Cluster Tags Based on Embeddings
# -------------------------------
def cluster_tags(embeddings, tags, num_clusters=20):
    """Cluster tags using KMeans."""
    log.info(f"Clustering tags into {num_clusters} clusters.")
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    kmeans.fit(embeddings)

    # Group tags by cluster label
    clusters = {}
    for i, label in enumerate(kmeans.labels_):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(tags[i])

    return clusters

# -------------------------------
# Generate Cluster Labels
# -------------------------------
def generate_cluster_labels(clusters):
    """Assign meaningful labels to each cluster based on common terms."""
    cluster_labels = {}
    
    for cluster, tag_list in clusters.items():
        # Tokenize and count common words across all tags in the cluster
        word_counter = Counter()
        for tag in tag_list:
            doc = nlp(tag.replace('-', ' '))
            for token in doc:
                if token.is_alpha and not token.is_stop:
                    word_counter[token.lemma_.lower()] += 1
        
        # Use the most common words to create a label for the cluster
        common_words = [word for word, count in word_counter.most_common(2)]  # Pick top 2 words
        cluster_labels[cluster] = "-".join(common_words) if common_words else f"cluster-{cluster}"
    
    return cluster_labels

# -------------------------------
# Save Grouped Tags with Labels to YAML
# -------------------------------
def save_clustered_tags_to_yaml(clusters, cluster_labels, output_file):
    """Save clustered tags to a YAML file with labeled clusters."""
    labeled_clusters = {cluster_labels[k]: v for k, v in clusters.items()}
    
    with open(output_file, 'w') as f:
        yaml.dump({'grouped_tags': labeled_clusters}, f, default_flow_style=False)
    log.info(f"Grouped tags saved to {output_file}")

# -------------------------------
# Main Process
# -------------------------------
def process_tags_for_clustering():
    """Load tags, generate embeddings, cluster tags, and save the results."""
    yaml_file = DATA_DIR / 'unique_tags.yaml'
    output_file = DATA_DIR / 'labeled_clustered_tags.yaml'

    # Step 1: Load tags
    tags = load_tags(yaml_file)
    log.info(f"Loaded {len(tags)} tags from {yaml_file}")

    # Step 2: Generate embeddings for tags
    embeddings = generate_embeddings(tags)

    # Step 3: Cluster tags
    num_clusters = 20  # Adjust number of clusters as needed
    clustered_tags = cluster_tags(embeddings, tags, num_clusters)

    # Step 4: Generate meaningful cluster labels
    cluster_labels = generate_cluster_labels(clustered_tags)

    # Step 5: Save the clustered tags with labels to a YAML file
    save_clustered_tags_to_yaml(clustered_tags, cluster_labels, output_file)

if __name__ == "__main__":
    log.info("Starting ML-based tag clustering process.")
    process_tags_for_clustering()
    log.info("Finished tag clustering process.")
