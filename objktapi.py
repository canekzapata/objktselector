import requests
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

# Archivos JSON
DATA_FILE = 'objkt_data.json'  # Búsquedas completas
COLLECTION_FILE = 'my_collection.json'  # Piezas seleccionadas

def load_saved_data():
    """Carga los datos guardados del archivo JSON"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_collection():
    """Carga la colección personal"""
    try:
        with open(COLLECTION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_to_collection(token_data):
    """Guarda un token en la colección personal"""
    collection = load_collection()
    
    # Evitar duplicados
    token_id = token_data.get('token_id')
    if not any(t.get('token_id') == token_id for t in collection):
        token_data['added_at'] = datetime.datetime.now().isoformat()
        collection.append(token_data)
        
        with open(COLLECTION_FILE, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        return True
    return False

def remove_from_collection(token_id):
    """Elimina un token de la colección personal"""
    collection = load_collection()
    original_length = len(collection)
    collection = [t for t in collection if t.get('token_id') != token_id]
    
    if len(collection) < original_length:
        with open(COLLECTION_FILE, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        return True
    return False

def save_data(address, data):
    """Guarda los datos en el archivo JSON - solo el historial de búsqueda"""
    all_data = load_saved_data()
    all_data[address] = {
        'timestamp': data.get('timestamp'),
        'count': data.get('count', 0)  # Solo guardamos el conteo, no los tokens completos
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

def get_artist_tokens(address):
    """Obtiene los tokens de un artista desde la API de Objkt"""
    url = "https://data.objkt.com/v3/graphql"
    
    query = """
    query GetArtistTokens($address: String!) {
      token(where: {creators: {creator_address: {_eq: $address}}}, order_by: {timestamp: desc}, limit: 500) {
        token_id
        name
        description
        supply
        display_uri
        thumbnail_uri
        artifact_uri
        mime
        timestamp
        fa_contract
        listings(where: {status: {_eq: "active"}}, order_by: {price: asc}, limit: 1) {
          price
          currency {
            symbol
            decimals
          }
        }
      }
    }
    """
    
    variables = {"address": address}
    
    try:
        response = requests.post(url, json={'query': query, 'variables': variables})
        response.raise_for_status()
        data = response.json()
        
        if 'errors' in data:
            return {'error': str(data['errors'])}
        
        tokens = data.get('data', {}).get('token', [])
        
        # Procesar los tokens
        processed_tokens = []
        for token in tokens:
            # Obtener el precio más bajo
            price = None
            if token['listings']:
                listing = token['listings'][0]
                decimals = listing['currency']['decimals']
                price_raw = int(listing['price'])
                price = price_raw / (10 ** decimals)
                currency = listing['currency']['symbol']
                price = f"{price} {currency}"
            
            # Determinar la URL del asset
            asset_url = token.get('display_uri') or token.get('artifact_uri') or token.get('thumbnail_uri') or ''
            if asset_url and asset_url.startswith('ipfs://'):
                asset_url = asset_url.replace('ipfs://', 'https://ipfs.io/ipfs/')
            
            thumbnail_url = token.get('thumbnail_uri') or ''
            if thumbnail_url and thumbnail_url.startswith('ipfs://'):
                thumbnail_url = thumbnail_url.replace('ipfs://', 'https://ipfs.io/ipfs/')
            
            processed_tokens.append({
                'token_id': token['token_id'],
                'name': token['name'] or f"Token #{token['token_id']}",
                'description': token['description'],
                'supply': token['supply'],
                'mime': token['mime'],
                'asset_url': asset_url,
                'thumbnail_url': thumbnail_url,
                'price': price,
                'timestamp': token['timestamp'],
                'objkt_url': f"https://objkt.com/tokens/{token.get('fa_contract', 'KT1RJ6PbjHpwc3M5rw5s2Nbmefwbuwbdxton')}/{token['token_id']}"
            })
        
        return {
            'success': True,
            'tokens': processed_tokens,
            'count': len(processed_tokens)
        }
    
    except requests.exceptions.RequestException as e:
        return {'error': f'Error de conexión: {str(e)}'}
    except Exception as e:
        return {'error': f'Error inesperado: {str(e)}'}

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/get-tokens', methods=['POST'])
def api_get_tokens():
    """API endpoint para obtener tokens de un artista"""
    data = request.get_json()
    address = data.get('address', '').strip()
    
    if not address:
        return jsonify({'error': 'Dirección requerida'}), 400
    
    result = get_artist_tokens(address)
    
    if result.get('success'):
        # Guardar solo info básica de búsqueda en JSON (no los tokens completos)
        save_data(address, {
            'timestamp': datetime.datetime.now().isoformat(),
            'count': result.get('count', 0)  # Usar .get() para evitar KeyError
        })
    
    return jsonify(result)

@app.route('/api/saved-data')
def api_saved_data():
    """API endpoint para obtener los datos guardados"""
    return jsonify(load_saved_data())

@app.route('/api/collection', methods=['GET'])
def api_get_collection():
    """API endpoint para obtener la colección personal"""
    return jsonify({'collection': load_collection(), 'count': len(load_collection())})

@app.route('/api/collection/add', methods=['POST'])
def api_add_to_collection():
    """API endpoint para agregar un token a la colección"""
    token_data = request.get_json()
    
    if save_to_collection(token_data):
        return jsonify({'success': True, 'message': 'Agregado a tu colección'})
    else:
        return jsonify({'success': False, 'message': 'Ya está en tu colección'})

@app.route('/api/collection/remove', methods=['POST'])
def api_remove_from_collection():
    """API endpoint para eliminar un token de la colección"""
    data = request.get_json()
    token_id = data.get('token_id')
    
    if remove_from_collection(token_id):
        return jsonify({'success': True, 'message': 'Eliminado de tu colección'})
    else:
        return jsonify({'success': False, 'message': 'No se encontró en tu colección'})

if __name__ == '__main__':
    print("🚀 Servidor iniciado en http://localhost:5000")
    print("📁 Búsquedas completas → objkt_data.json")
    print("⭐ Tu colección personal → my_collection.json")
    print("📂 Asegúrate de tener el archivo index.html en la carpeta templates/")
    app.run(debug=True, port=5000)
