#!/usr/bin/env python3
"""
Production-ready Flask web application for Telegram message link generation
Compatible with Render.com free deployment
"""

import os
import sys
import uuid
import time
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
from urllib.parse import urlencode
import secrets
import json
from werkzeug.utils import secure_filename

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Flask to use templates from current directory
app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Configuration
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# In-memory storage for demonstration (use database in production)
generated_links = {}  # Store active links
admin_data = {}  # Store all generated data

class TelegramBot:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, chat_id, text):
        """Send message via Telegram Bot API"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def get_bot_info(self):
        """Get bot information"""
        url = f"{self.base_url}/getMe"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting bot info: {e}")
            return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def home():
    """Home page with form to generate links"""
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return redirect(url_for('admin_dashboard'))
    
    stats = {
        'total_links': len([link for link in generated_links.values() if not link['used']]),
        'total_messages': sum(len(link.get('sent_messages', [])) for link in generated_links.values()),
        'active_admins': len(set(link['admin_id'] for link in generated_links.values()))
    }
    
    return render_template('home_simple.html', stats=stats)

@app.route('/generate_link', methods=['POST'])
def generate_link():
    """Generate unique link for message sending"""
    bot_token = request.form.get('bot_token', '').strip()
    admin_id = request.form.get('admin_id', '').strip()
    
    if not bot_token or not admin_id:
        flash('Bot Token and Admin ID are required!', 'error')
        return redirect(url_for('home'))
    
    # Validate bot token format (should be numbers:long_alphanumeric_string)
    if ':' not in bot_token:
        flash('Invalid bot token format! Must contain a colon (:)', 'error')
        return redirect(url_for('home'))
    
    parts = bot_token.split(':', 1)
    if len(parts) != 2:
        flash('Invalid bot token format!', 'error')
        return redirect(url_for('home'))
    
    # Check if first part is numbers and second part has reasonable length
    if not parts[0].isdigit() or len(parts[1]) < 20:
        flash('Invalid bot token format!', 'error')
        return redirect(url_for('home'))
    
    # Validate admin ID format
    if not admin_id.isdigit():
        flash('Admin ID must be a numeric value!', 'error')
        return redirect(url_for('home'))
    
    # Test bot token
    bot = TelegramBot(bot_token)
    bot_info = bot.get_bot_info()
    if not bot_info or not bot_info.get('ok'):
        flash('Invalid bot token! Please check your bot token.', 'error')
        return redirect(url_for('home'))
    
    # Generate unique link ID
    link_id = str(uuid.uuid4()).replace('-', '').upper()[:8]
    unique_link = f"/send/{link_id}"
    
    # Store link data with expiration (24 hours)
    expiration_time = datetime.now() + timedelta(hours=24)
    
    generated_links[link_id] = {
        'bot_token': bot_token,
        'admin_id': admin_id,
        'created_at': datetime.now().isoformat(),
        'expiration_time': expiration_time.isoformat(),
        'used': False,
        'sent_messages': [],
        'bot_username': bot_info.get('result', {}).get('username', 'Unknown')
    }
    
    # Store in admin data
    admin_data[admin_id] = admin_data.get(admin_id, {})
    admin_data[admin_id]['links'] = admin_data[admin_id].get('links', [])
    admin_data[admin_id]['links'].append({
        'link_id': link_id,
        'link_url': unique_link,
        'created_at': datetime.now().isoformat(),
        'used': False,
        'bot_username': bot_info.get('result', {}).get('username', 'Unknown')
    })
    
    # Store bot token for admin
    if 'bot_tokens' not in admin_data[admin_id]:
        admin_data[admin_id]['bot_tokens'] = []
    if bot_token not in admin_data[admin_id]['bot_tokens']:
        admin_data[admin_id]['bot_tokens'].append(bot_token)
    
    return render_template('link_generated_simple.html', link=unique_link, link_id=link_id)

@app.route('/send/<link_id>', methods=['GET', 'POST'])
def send_messages(link_id):
    """Message sending page"""
    # Check if link exists and is not expired
    if link_id not in generated_links:
        return render_template('link_expired_simple.html', message="This link does not exist!")
    
    link_data = generated_links[link_id]
    
    # Check if link is expired
    expiration_time = datetime.fromisoformat(link_data['expiration_time'])
    if datetime.now() > expiration_time:
        return render_template('link_expired_simple.html', message="This link has expired!")
    
    # Check if link was already used
    if link_data['used']:
        return render_template('link_expired_simple.html', message="This link is Expired!")
    
    if request.method == 'POST':
        message1 = request.form.get('message1', '').strip()
        message2 = request.form.get('message2', '').strip()
        
        if not message1 and not message2:
            flash('Please enter at least one message!', 'error')
            return render_template('send_message_simple.html', link_id=link_id, messages_sent=False)
        
        # Send messages via Telegram bot
        bot = TelegramBot(link_data['bot_token'])
        
        combined_message = f"📨 <b>New Message Received</b>\n\n"
        if message1:
            combined_message += f"🔸 <b>Message 1:</b> {message1}\n\n"
        if message2:
            combined_message += f"🔹 <b>Message 2:</b> {message2}\n\n"
        combined_message += f"⏰ <b>Sent at:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        combined_message += f"🤖 <b>Bot:</b> @{link_data.get('bot_username', 'Unknown')}"
        
        success = bot.send_message(link_data['admin_id'], combined_message)
        
        if success:
            # Mark link as used
            link_data['used'] = True
            link_data['sent_at'] = datetime.now().isoformat()
            link_data['sent_messages'] = [message1, message2]
            
            # Update admin data
            for admin_id_key, data in admin_data.items():
                for link_info in data.get('links', []):
                    if link_info['link_id'] == link_id:
                        link_info['used'] = True
                        link_info['sent_at'] = datetime.now().isoformat()
                        link_info['messages'] = [message1, message2]
            
            return render_template('message_sent_simple.html')
        else:
            flash('Failed to send messages. Please check your bot token and admin ID.', 'error')
            return render_template('send_message_simple.html', link_id=link_id, messages_sent=False)
    
    return render_template('send_message_simple.html', link_id=link_id, messages_sent=False)

@app.route('/api/link')
def api_generate_link():
    """API endpoint to generate link via GET request"""
    try:
        admin_id = request.args.get('admin_id', '').strip()
        bot_token = request.args.get('token', '').strip()
        
        if not admin_id or not bot_token:
            return jsonify({'error': 'admin_id and token parameters are required'}), 400
        
        # Validate bot token format (should be numbers:long_alphanumeric_string)
        if ':' not in bot_token:
            return jsonify({'error': 'Invalid bot token format! Must contain a colon (:)'}), 400
        
        parts = bot_token.split(':', 1)
        if len(parts) != 2:
            return jsonify({'error': 'Invalid bot token format!'}), 400
        
        # Check if first part is numbers and second part has reasonable length
        if not parts[0].isdigit() or len(parts[1]) < 20:
            return jsonify({'error': 'Invalid bot token format!'}), 400
        
        # Validate admin ID format
        if not admin_id.isdigit():
            return jsonify({'error': 'Admin ID must be numeric'}), 400
        
        # Test bot token
        bot = TelegramBot(bot_token)
        bot_info = bot.get_bot_info()
        if not bot_info or not bot_info.get('ok'):
            return jsonify({'error': 'Invalid bot token'}), 400
        
        # Generate unique link ID
        link_id = str(uuid.uuid4()).replace('-', '').upper()[:8]
        unique_link = f"/send/{link_id}"
        
        # Store link data with expiration (24 hours)
        expiration_time = datetime.now() + timedelta(hours=24)
        
        generated_links[link_id] = {
            'bot_token': bot_token,
            'admin_id': admin_id,
            'created_at': datetime.now().isoformat(),
            'expiration_time': expiration_time.isoformat(),
            'used': False,
            'sent_messages': [],
            'bot_username': bot_info.get('result', {}).get('username', 'Unknown')
        }
        
        # Store in admin data
        admin_data[admin_id] = admin_data.get(admin_id, {})
        admin_data[admin_id]['links'] = admin_data[admin_id].get('links', [])
        admin_data[admin_id]['links'].append({
            'link_id': link_id,
            'link_url': unique_link,
            'created_at': datetime.now().isoformat(),
            'used': False,
            'bot_username': bot_info.get('result', {}).get('username', 'Unknown')
        })
        
        # Store bot token for admin
        if 'bot_tokens' not in admin_data[admin_id]:
            admin_data[admin_id]['bot_tokens'] = []
        if bot_token not in admin_data[admin_id]['bot_tokens']:
            admin_data[admin_id]['bot_tokens'].append(bot_token)
        
        return jsonify({
            'success': True,
            'link_id': link_id,
            'link_url': unique_link,
            'expires_at': expiration_time.isoformat(),
            'bot_username': bot_info.get('result', {}).get('username', 'Unknown')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
def admin_login():
    """Admin login page"""
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login_simple.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_submit():
    """Admin login submission"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if username == 'mk' and password == 'mk123':
        session['admin_logged_in'] = True
        session['admin_username'] = username
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid credentials!', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard to view all data"""
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('admin_login'))
    
    # Calculate statistics
    total_links = len([link for link in generated_links.values() if not link['used']])
    total_used_links = len([link for link in generated_links.values() if link['used']])
    total_messages = len([link for link in generated_links.values() if link['sent_messages']])
    
    stats = {
        'total_links': total_links,
        'total_used_links': total_used_links,
        'total_messages': total_messages,
        'active_admins': len(set(link['admin_id'] for link in generated_links.values()))
    }
    
    return render_template('admin_dashboard_simple.html', admin_data=admin_data, stats=stats)

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_links': len(generated_links),
        'admin_count': len(admin_data)
    })

@app.route('/admin/links/<admin_id>')
def admin_view_links(admin_id):
    """View links for specific admin"""
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('admin_login'))
    
    admin_links = admin_data.get(admin_id, {}).get('links', [])
    return jsonify({'links': admin_links})

@app.route('/cleanup')
def cleanup_expired_links():
    """Clean up expired links"""
    current_time = datetime.now()
    expired_links = []
    
    for link_id, link_data in list(generated_links.items()):
        expiration_time = datetime.fromisoformat(link_data['expiration_time'])
        if current_time > expiration_time or link_data['used']:
            expired_links.append(link_id)
    
    for link_id in expired_links:
        del generated_links[link_id]
    
    return jsonify({
        'cleaned': len(expired_links),
        'remaining_active': len(generated_links),
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404_simple.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500_simple.html'), 500

# Production WSGI application
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )