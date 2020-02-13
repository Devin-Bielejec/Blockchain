import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS
DIFFICULTY = 6

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # Create the genesis block, 1 is very different from all the other data
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain-1)
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string, sort keys in python3.7 sort automatically, but we could be getting old data
        block_string = json.dumps(block, sort_keys=True).encode()

        # TODO: Hash this string using sha256, requires byte object not actual string
        hash = hashlib.sha256(block_string).hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hash

    @property
    def last_block(self):
        return self.chain[-1]

    # def proof_of_work(self, block):
    #     """
    #     Simple Proof of Work Algorithm
    #     Stringify the block and look for a proof.
    #     Loop through possibilities, checking each one against `valid_proof`
    #     in an effort to find a number that is a valid proof
    #     :return: A valid proof for the provided block
    #     """
    #     # TODO
    #     block_string = json.dumps(self.last_block, sort_keys=True)
    #     # So this user is trying to add block_string + a number to see if they can find a hash with 6 leadings 0's, then if they find the proof, then they can send their proof (ie some large number) and the server can verify the proof by doing the oringal hash and compare hashes?
    #     proof = 0
    #     while self.valid_proof(block_string, proof) is False:
    #         proof += 1

    #     #Are you returning a number to show how many you checked - to show the work put in
    #     return proof

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        # TODO
        guess = f"{block_string}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:DIFFICULTY] == "0" * DIFFICULTY


# Instantiate our Node
app = Flask(__name__)
CORS(app)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route("/maze/<size>", methods=["GET"])
def get_maze(size):
    size = int(size)
    import random
 
    def getAdjacentRooms(board, rowIdx, colIdx):
        adjacent_rooms = []
        vectors = [[0,1],[0,-1],[1,0],[-1,0]]
        for [r,c] in vectors:
            if rowIdx + r >= 0 and rowIdx + r < len(board) and colIdx + c >= 0 and colIdx + c < len(board):
                adjacent_rooms.append(board[rowIdx+r][colIdx+c]) 
        return adjacent_rooms


    #rooms are objects {visited, coordinates}
    #We're going to add exits: {north, south, east, west etc}
    def addExits(room1, room2):
        #north (row=0) south (row >) 
        if room1["coordinates"][0] > room2["coordinates"][0]:
            room1["exits"].append("north")
            room2["exits"].append("south")

        #south north
        if room1["coordinates"][0] < room2["coordinates"][0]:
            room1["exits"].append("south")
            room2["exits"].append("north")
        
        #east west - col < secondCol
        if room1["coordinates"][1] < room2["coordinates"][1]:
            room1["exits"].append("east")
            room2["exits"].append("west")

        #west east
        if room1["coordinates"][1] > room2["coordinates"][1]:
            room1["exits"].append("west")
            room2["exits"].append("east")

    def make_maze_objects(size):
        maze = []
        names = ["The Kitchen", "Basement", "Garden", "Den"]
        descriptions = ["SO quiet", "so cold", "so hot"]
        for i in range(size):
            #Adding a row
            maze.append([])
            for j in range(size):
                #for each column add an object
                maze[i].append({"name": random.choice(names), "description": random.choice(descriptions),"isChicken": False, "players": [], "coordinates": [i,j], "visited": False, "exits": []})

        return maze


    def make_maze(size):
        maze = make_maze_objects(size)

        #Holding previous_room, current_room
        stack = [[None, maze[0][0]]]
        while stack:
            [previous_room, current_room] = stack.pop()

            if current_room["visited"]:
                #Then i want to make a door for previous and current room
                continue
            else:
                #If previous room is not None, make exits for both rooms
                if previous_room is not None:
                    addExits(previous_room, current_room)

                #Make current_room visited
                current_room["visited"] = True
                #get list of adjacent rooms
                adjacent_rooms = getAdjacentRooms(maze, current_room["coordinates"][0], current_room["coordinates"][1])
                
                #randomize adjacent rooms and add to stack if they haven't been visited
                random.shuffle(adjacent_rooms)
                for adj_room in adjacent_rooms:
                    if adj_room["visited"] is False:
                        #previous_room => current_room
                        #current_room => adj
                        stack.append([current_room, adj_room])

        return maze
    maze = make_maze(size)

    for i in range(len(maze)):
        for j in range(len(maze[i])):
            del maze[i][j]["visited"]


    return jsonify(maze), 200

@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()

    # Check that proof and id are present
    if not data["proof"] or not data["id"]:
        response = {
            "message": "Failure"
        }
        return jsonify(response), 400
    
    block_string = json.dumps(blockchain.last_block, sort_keys=True)

    #We need to check if the proof matches for the last block
    if blockchain.valid_proof(block_string, data["proof"]):
        # Forge the new Block by adding it to the chain with the proof
        previous_hash = blockchain.hash(blockchain.last_block)
        new_block = blockchain.new_block(data["proof"], previous_hash)
        
        # TODO: Send a JSON response with the new block
        response = {
            "message": "New Block Forged",
            "block": new_block,   
            "coins": 1 
        }

        return jsonify(response), 200

@app.route('/last_block', methods=['Get'])
def last_block():
    response = {
        "block": blockchain.last_block
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    # TODO: Return the chain and its current length
    response = {
        "length": len(blockchain.chain),
        "chain": blockchain.chain
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
