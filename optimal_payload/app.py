from flask import Flask, jsonify, request

app = Flask(__name__)

global_limit = 5093


@app.route('/numbers', methods=['POST'])
def set_limit():
    global global_limit
    limit_param = request.args.get('limit', None)

    if limit_param is None:
        return jsonify({"error": "No limit provided in query parameters"}), 400

    try:
        limit_param = int(limit_param)
    except ValueError:
        return jsonify({"error": "Invalid limit value"}), 400

    global_limit = limit_param
    return jsonify({"message": f"Global limit set to {global_limit}"}), 200


@app.route('/numbers', methods=['GET'])
def get_numbers():
    global global_limit
    limit_param = request.args.get('limit', None)

    if limit_param is None:
        return jsonify({"error": "No limit provided in query parameters"}), 400

    try:
        limit_param = int(limit_param)
    except ValueError:
        return jsonify({"error": "Invalid limit value"}), 400

    if limit_param > global_limit:
        return jsonify({"error": f"Limit exceeds the global limit"}), 400

    numbers = list(range(1, limit_param + 1))
    return jsonify({"numbers": numbers}), 200


if __name__ == '__main__':
    app.run(debug=True)
