from flask import Flask, render_template, request, jsonify
from analyze import PrizePicskAnalyzer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    sport = data.get('sport')
    player = data.get('player')
    line = float(data.get('line', 0))

    analyzer = PrizePicskAnalyzer(sport)
    result = analyzer.analyze_player(player, line)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
