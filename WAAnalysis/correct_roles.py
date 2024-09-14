import logging
import yaml
from pathlib import Path
from WAAnalysis.utils import load_markdown, update_markdown_frontmatter
from WAAnalysis.config import MD_DIR

# -------------------------------
# Setup Logging
# -------------------------------
log = logging.getLogger(__name__)

# -------------------------------
# Role Update and Name Correction Mapping
# -------------------------------
ROLE_MAPPING = {
    "Ana": "daughter",   # Correct spelling
    "Bella": "daughter",
    "Elizabeth": "mother",
    "Jason": "father",
    "Kylie": "Jason's cousin",
    "Leanne": "Jason's cousin",
    "Amanda": "Elizabeth's cousin",
    "Bells": "daughter",  # another name for Bella
    "Jeff": "Jason's friend",
    "Jon": "Jason's friend",
    "Nazira": "Counsellor",
    "Gloria": "Counsellor",
    "Lizzy": "mother",  # another name for Elizabeth
    "Wesley": "dog",
    "Nathan": "Jason's surname",
    "Yvonne": "Jason's sister",
    "Francois": "Jason's boss",
    "Su": "Elizabeth's friend",
    "Kevin": "Su's Husband"
}

# -------------------------------
# Update Names and Roles in Entity Relationships
# -------------------------------
def update_entity_relationships(entity_relationships):
    """Updates the person name from 'Anna' to 'Ana' and their corresponding roles."""
    updated_entities = []
    for entity in entity_relationships:
        person = entity.get('person')
        
        # Correct any instances of 'Anna' to 'Ana'
        if person == "Anna":
            log.debug(f"Correcting name from 'Anna' to 'Ana'")
            person = "Ana"  # Update the name to 'Ana'
        
        # Update the role based on the person
        if person in ROLE_MAPPING:
            log.debug(f"Updating role for {person} to {ROLE_MAPPING[person]}")
            entity['person'] = person
            entity['role'] = ROLE_MAPPING[person]  # Update the role if person matches
        
        updated_entities.append(entity)
    
    return updated_entities

# -------------------------------
# Process Markdown Files to Update Roles and Names
# -------------------------------
def process_markdown_for_entity_relationships():
    """Iterate over markdown files and update entity_relationships' names and roles."""
    md_files = [f for f in MD_DIR.iterdir() if f.suffix == '.md']

    for file in md_files:
        log.info(f"Processing file: {file}")
        frontmatter, body = load_markdown(file)

        entity_relationships = frontmatter.get('entity_relationships', [])
        if entity_relationships:
            log.debug(f"Original entity_relationships for {file}: {entity_relationships}")

            # Update the names and roles in entity_relationships
            updated_entities = update_entity_relationships(entity_relationships)
            frontmatter['entity_relationships'] = updated_entities

            log.debug(f"Updated entity_relationships for {file}: {updated_entities}")
            update_markdown_frontmatter(file, frontmatter)
            log.info(f"Updated names and roles for {file}")

if __name__ == "__main__":
    log.info("Starting process to update names and roles in entity_relationships.")
    process_markdown_for_entity_relationships()
    log.info("Finished updating names and roles in entity_relationships.")
