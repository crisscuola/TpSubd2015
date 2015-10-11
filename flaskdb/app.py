from flask import Flask, jsonify
app = Flask(__name__)
 
@app.route('/')
def index():
    return 'Flask is running! TP_DB_2015'
 
@app.route('/data')
def names():
    data = {"names": ["John", "Jacob", "Julie", "Jennifer"]}
    return jsonify(data)
 
if __name__ == '__main__':
    app.run()
