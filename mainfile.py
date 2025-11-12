import os
import uuid
import time
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta
from urllib.parse import urlencode
import secrets
import json

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

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
            response = requests.post(url, data=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

@app.route('/')
def home():
    """Home page with form to generate links"""
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return redirect(url_for('admin_dashboard'))
    return render_template('home.html')

@app.route('/generate_link', methods=['POST'])
def generate_link():
    """Generate unique link for message sending"""
    bot_token = request.form.get('bot_token', '').strip()
    admin_id = request.form.get('admin_id', '').strip()
    
    if not bot_token or not admin_id:
        flash('Bot Token and Admin ID are required!', 'error')
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
        'sent_messages': []
    }
    
    # Store in admin data
    admin_data[admin_id] = admin_data.get(admin_id, {})
    admin_data[admin_id]['links'] = admin_data[admin_id].get('links', [])
    admin_data[admin_id]['links'].append({
        'link_id': link_id,
        'link_url': unique_link,
        'created_at': datetime.now().isoformat(),
        'used': False
    })
    
    # Store bot token for admin (if not already stored)
    if 'bot_tokens' not in admin_data[admin_id]:
        admin_data[admin_id]['bot_tokens'] = []
    if bot_token not in admin_data[admin_id]['bot_tokens']:
        admin_data[admin_id]['bot_tokens'].append(bot_token)
    
    return render_template('link_generated.html', link=unique_link, link_id=link_id)

@app.route('/send/<link_id>')
def send_messages(link_id):
    """Message sending page"""
    # Check if link exists and is not expired
    if link_id not in generated_links:
        return render_template('link_expired.html', message="This link does not exist!")
    
    link_data = generated_links[link_id]
    
    # Check if link is expired
    expiration_time = datetime.fromisoformat(link_data['expiration_time'])
    if datetime.now() > expiration_time:
        return render_template('link_expired.html', message="This link has expired!")
    
    # Check if link was already used
    if link_data['used']:
        return render_template('link_expired.html', message="This link is Expired!")
    
    if request.method == 'POST':
        message1 = request.form.get('message1', '').strip()
        message2 = request.form.get('message2', '').strip()
        
        if not message1 and not message2:
            flash('Please enter at least one message!', 'error')
            return render_template('send_message.html', link_id=link_id, messages_sent=False)
        
        # Send messages via Telegram bot
        bot = TelegramBot(link_data['bot_token'])
        
        combined_message = f"📨 New Message Received:\n\n"
        if message1:
            combined_message += f"Message 1: {message1}\n\n"
        if message2:
            combined_message += f"Message 2: {message2}\n\n"
        combined_message += f"⏰ Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        success = bot.send_message(link_data['admin_id'], combined_message)
        
        if success:
            # Mark link as used
            link_data['used'] = True
            link_data['sent_at'] = datetime.now().isoformat()
            link_data['sent_messages'] = [message1, message2]
            
            # Update admin data
            for admin_id, data in admin_data.items():
                for link_info in data.get('links', []):
                    if link_info['link_id'] == link_id:
                        link_info['used'] = True
                        link_info['sent_at'] = datetime.now().isoformat()
                        link_info['messages'] = [message1, message2]
            
            return render_template('message_sent.html')
        else:
            flash('Failed to send messages. Please check your bot token and admin ID.', 'error')
            return render_template('send_message.html', link_id=link_id, messages_sent=False)
    
    return render_template('send_message.html', link_id=link_id, messages_sent=False)

@app.route('/api/link')
def api_generate_link():
    """API endpoint to generate link via GET request"""
    try:
        admin_id = request.args.get('admin_id', '').strip()
        bot_token = request.args.get('token', '').strip()
        
        if not admin_id or not bot_token:
            return jsonify({'error': 'admin_id and token parameters are required'}), 400
        
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
            'sent_messages': []
        }
        
        # Store in admin data
        admin_data[admin_id] = admin_data.get(admin_id, {})
        admin_data[admin_id]['links'] = admin_data[admin_id].get('links', [])
        admin_data[admin_id]['links'].append({
            'link_id': link_id,
            'link_url': unique_link,
            'created_at': datetime.now().isoformat(),
            'used': False
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
            'expires_at': expiration_time.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
def admin_login():
    """Admin login page"""
    return render_template('admin_login.html')

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
    
    return render_template('admin_dashboard.html', admin_data=admin_data)

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/cleanup')
def cleanup_expired_links():
    """Clean up expired links (can be called by keep_alive)"""
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
        'remaining_active': len(generated_links)
    })

# Template rendering functions
def render_template(template_name, **kwargs):
    """Custom template renderer"""
    template_path = os.path.join('templates', template_name)
    if not os.path.exists(template_path):
        return create_template_file(template_name)
    
    # For now, return basic template content
    return f"Template: {template_name}"

def create_template_file(template_name):
    """Create template file if it doesn't exist"""
    return f"Template {template_name} will be created separately"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)