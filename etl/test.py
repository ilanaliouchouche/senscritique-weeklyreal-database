from dotenv import load_dotenv
import os
import requests
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def get_embeddings(reviews):
        embeddings = []
        print("Computing embeddings...")

        for r in reviews:
            response = requests.post(f"http://{os.getenv('TEI_HOSTNAME')}:{os.getenv('TEI_HPORT')}/embed", json={
            "inputs": r,
            "normalize": True,
            "truncate": False
            })
            if response.status_code == 200:
                embeddings.extend(response.json())
            else:
                embeddings.append(None)
        print("Done with embeddings")

        return embeddings