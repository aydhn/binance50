with open("binance50/src/binance50/portfolio/sandbox/similarity.py", "r") as f:
    content = f.read()

content = content.replace("from scipy.spatial.distance import pdist, squareform", "try:\n        from scipy.spatial.distance import pdist, squareform\n    except ImportError:\n        return pd.DataFrame(np.eye(len(vectors)), index=vectors.index, columns=vectors.index)")

with open("binance50/src/binance50/portfolio/sandbox/similarity.py", "w") as f:
    f.write(content)
