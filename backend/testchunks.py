import pickle
import os

# Set the name of the document you uploaded
DOC_NAME = "Researchpaper1.pdf" 
PKL_PATH = os.path.join("vector_store", f"{DOC_NAME}.pkl")

def inspect_data():
    if not os.path.exists(PKL_PATH):
        print(f"❌ Error: {PKL_PATH} not found. Did you run the upload yet?")
        return

    try:
        with open(PKL_PATH, "rb") as f:
            chunks = pickle.load(f)
        
        print(f"✅ Successfully loaded {len(chunks)} chunks from {DOC_NAME}")
        print("-" * 50)
        
        # Print the first 3 chunks to verify content
        for i, chunk in enumerate(chunks[:3]):
            print(f"🔹 CHUNK {i+1}:")
            print(f"{chunk[:300]}...") # Show first 300 characters
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Failed to read pickle file: {e}")

if __name__ == "__main__":
    inspect_data()