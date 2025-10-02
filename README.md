# 🎨 Objkt NFT Explorer

Explorador web para visualizar y coleccionar NFTs de artistas en Objkt (Tezos).

## 🚀 Instalación Rápida

### 1. Requisitos
- Python 3.7+
- pip

### 2. Instalar dependencias
```bash
pip install flask flask-cors requests
```

### 3. Estructura de archivos
```
proyecto/
├── objapi.py           # Backend Python
├── templates/
│   └── index.html      # Frontend HTML
├── objkt_data.json     # Se crea automáticamente
└── my_collection.json  # Se crea automáticamente
```

### 4. Ejecutar
```bash
python objapi.py
```

Abre tu navegador en: **http://localhost:5000**

## 📖 Uso

1. **Buscar artista**: Ingresa la dirección Tezos del artista (ej: `tz1U8x9dUtdv4mtLUvaukpMNVi1wvNxr1gy2`)
2. **Ver NFTs**: Explora todos los tokens del artista
3. **Guardar favoritos**: Click en 🤍 para agregar a tu colección
4. **Ver colección**: Click en "⭐ Mi Colección" para ver tus NFTs guardados

## 📁 Archivos JSON

- **objkt_data.json**: Historial de búsquedas (solo info básica)
- **my_collection.json**: NFTs que guardaste manualmente

## 🎯 Características

- ✅ Búsqueda por dirección de artista
- ✅ Visualización de imágenes, GIFs y videos
- ✅ Filtros por tipo de contenido
- ✅ Información de precios y ediciones
- ✅ Colección personal selectiva
- ✅ Enlaces directos a Objkt.com

## 🌐 Desplegar en Producción

### DigitalOcean (Droplet)

1. **Crear servidor Ubuntu 22.04**
2. **Instalar dependencias**:
```bash
apt update && apt upgrade -y
apt install python3 python3-pip nginx -y
pip3 install flask flask-cors requests gunicorn
```

3. **Subir archivos** (vía SCP, FileZilla o WinSCP)

4. **Crear servicio systemd** (`/etc/systemd/system/objkt.service`):
```ini
[Unit]
Description=Objkt NFT Explorer
After=network.target

[Service]
User=root
WorkingDirectory=/root
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:5000 objapi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Configurar Nginx** (`/etc/nginx/sites-available/objkt`):
```nginx
server {
    listen 80;
    server_name tu_dominio_o_ip;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. **Activar todo**:
```bash
ln -s /etc/nginx/sites-available/objkt /etc/nginx/sites-enabled/
systemctl start objkt
systemctl enable objkt
systemctl restart nginx
ufw allow 80
ufw allow 22
ufw enable
```

### Cambios para producción

En `objapi.py`, cambia:
```python
app.run(host='0.0.0.0', port=5000)
```

En `templates/index.html`, cambia todas las URLs:
```javascript
// De:
fetch('http://localhost:5000/api/...')

// A:
fetch('/api/...')
```

## 🛠️ API Endpoints

- `GET /` - Página principal
- `POST /api/get-tokens` - Obtener tokens de un artista
- `GET /api/collection` - Ver tu colección
- `POST /api/collection/add` - Agregar NFT a colección
- `POST /api/collection/remove` - Eliminar NFT de colección
- `GET /api/saved-data` - Historial de búsquedas

## 🐛 Troubleshooting

**Error: Template not found**
- Asegúrate de tener la carpeta `templates/` con `index.html` dentro

**Error: CORS**
- Verifica que `flask-cors` esté instalado

**Error: Connection refused**
- Asegúrate de que el servidor esté corriendo en el puerto 5000

## 📝 Notas

- La API de Objkt tiene límite de 500 tokens por búsqueda
- Los tokens se guardan selectivamente (solo los que tu elijas)
- Los precios mostrados son los listados activos más bajos

## 👤 Autor

Creado con ❤️ para explorar el arte en Tezos

## 📄 Licencia

MIT - Úsalo como quieras 🎉
