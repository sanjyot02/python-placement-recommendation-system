import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import re
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_experience(experience):
    numbers = re.findall("\d+", experience)
    return [int(numbers[0]), int(numbers[-1])] if numbers else [0, 0]

data = pd.read_csv("jobs_info.csv")
data["Experience Range"] = data["Job Experience"].apply(clean_experience)

skills_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
title_vectorizer = TfidfVectorizer(ngram_range=(1, 2))

tfidf_skills = skills_vectorizer.fit_transform(data["Key Skills"])
tfidf_titles = title_vectorizer.fit_transform(data["Job Title"])

def experience_similarity(candidate_exp, job_exp_range):
    # Adjust the similarity calculation for experience to smoothly handle ranges
    if candidate_exp < job_exp_range[0]:
        return max(0, 1 - (job_exp_range[0] - candidate_exp) / job_exp_range[0])
    elif candidate_exp > job_exp_range[1]:
        return max(0, 1 - (candidate_exp - job_exp_range[1]) / candidate_exp)
    else:
        return 1

def recommend_jobs(query_skills, query_title, query_experience):
    query_skills_vec = skills_vectorizer.transform([query_skills])
    query_title_vec = title_vectorizer.transform([query_title])

    skills_similarity = cosine_similarity(query_skills_vec, tfidf_skills).flatten()
    title_similarity = cosine_similarity(query_title_vec, tfidf_titles).flatten()

    # Normalize similarities
    skills_similarity = (skills_similarity - skills_similarity.min()) / (skills_similarity.max() - skills_similarity.min() + 1e-5)
    title_similarity = (title_similarity - title_similarity.min()) / (title_similarity.max() - title_similarity.min() + 1e-5)

    combined_similarity = (skills_similarity + title_similarity) / 2

    # Apply experience similarity and adjust combined score
    experience_scores = np.array([experience_similarity(query_experience, x) for x in data["Experience Range"]])
    combined_score = combined_similarity * experience_scores

    indices = np.argsort(-combined_score)[:10]
    if len(indices) == 0 or combined_score[indices[0]] == 0:  # Check if there are no recommendations
        return []

    results = data.iloc[indices]

    return results.to_dict(orient='records')

# Example usage
# results = recommend_jobs('java sql linux', 'software developer', 2)
# print(results)
# results = recommend_jobs('python sql', 'data analyst', 3)
# print(results)
