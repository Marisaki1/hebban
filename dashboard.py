# server_dashboard.py
"""
Simple dashboard to monitor Heaven Burns Red server
"""

import asyncio
import websockets
import json
from datetime import datetime
from src.networking.protocol import NetworkProtocol, MessageType

async def get_server_stats(host='localhost', port=8080):
    """Connect and get server statistics"""
    try:
        uri = f"ws://{host}:{port}"
        async with websockets.connect(uri) as websocket:
            # Send connect message
            await websocket.send(
                NetworkProtocol.create_message(
                    MessageType.CONNECT,
                    {
                        'player_id': 'dashboard',
                        'player_name': 'Dashboard',
                        'version': '1.0.0'
                    }
                )
            )
            
            # Wait for response
            response = await websocket.recv()
            msg_type, data = NetworkProtocol.parse_message(response)
            
            if msg_type == MessageType.CONNECT:
                server_info = data.get('server_info', {})
                
                # Request lobby list
                await websocket.send(
                    NetworkProtocol.create_message(MessageType.LOBBY_LIST, {})
                )
                
                # Wait for lobby list
                response = await websocket.recv()
                msg_type, data = NetworkProtocol.parse_message(response)
                
                if msg_type == MessageType.LOBBY_LIST:
                    lobbies = data.get('lobbies', [])
                    
                    # Print dashboard
                    print("\n" + "="*60)
                    print("HEAVEN BURNS RED - Server Dashboard")
                    print("="*60)
                    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Server: {host}:{port}")
                    print(f"Version: {server_info.get('version', 'Unknown')}")
                    print(f"Active Lobbies: {server_info.get('active_lobbies', 0)}/{server_info.get('max_lobbies', 20)}")
                    print()
                    
                    if lobbies:
                        print("Active Lobbies:")
                        print("-"*60)
                        print(f"{'Code':<8} {'Players':<10} {'Status':<15} {'Host ID':<20}")
                        print("-"*60)
                        
                        for lobby in lobbies:
                            status = "In Game" if lobby['game_started'] else "In Lobby"
                            players = f"{lobby['players']}/{lobby['max_players']}"
                            print(f"{lobby['code']:<8} {players:<10} {status:<15} {lobby['host']:<20}")
                    else:
                        print("No active lobbies")
                        
                    print("="*60)
                    
    except Exception as e:
        print(f"Error connecting to server: {e}")

async def monitor_server(host='localhost', port=8080, interval=5):
    """Monitor server continuously"""
    while True:
        # Clear screen (works on most terminals)
        print("\033[2J\033[H")
        
        await get_server_stats(host, port)
        await asyncio.sleep(interval)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Heaven Burns Red Server Dashboard')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    parser.add_argument('--once', action='store_true', help='Run once instead of monitoring')
    parser.add_argument('--interval', type=int, default=5, help='Update interval in seconds')
    
    args = parser.parse_args()
    
    try:
        if args.once:
            asyncio.run(get_server_stats(args.host, args.port))
        else:
            asyncio.run(monitor_server(args.host, args.port, args.interval))
    except KeyboardInterrupt:
        print("\nDashboard stopped")