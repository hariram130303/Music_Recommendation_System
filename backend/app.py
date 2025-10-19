#app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import get_recommendations

# Initialize the Flask app
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow frontend requests
CORS(app)

@app.route('/recommend', methods=['GET'])
def recommend():
    # Get the song title from the query parameters
    song_title = request.args.get('title')
    
    if not song_title:
        return jsonify({"error": "A 'title' parameter is required."}), 400
        
    # Get recommendations using our function
    recommendations = get_recommendations(song_title)
    
    return jsonify(recommendations)

if __name__ == '__main__':
    # Run the app on port 5000
    app.run(debug=True, port=5000)