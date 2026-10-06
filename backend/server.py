from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timedelta
import uuid
import random
import json
import asyncio
from typing import List, Dict, Optional
import numpy as np
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="5G IoT Security Monitor", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
devices_collection = db.devices
threats_collection = db.threats
network_logs_collection = db.network_logs

# Pydantic models
class Device(BaseModel):
    device_id: str
    device_name: str
    device_type: str
    ip_address: str
    mac_address: str
    location: str
    status: str
    last_seen: datetime
    security_score: float
    threat_level: str

class NetworkTraffic(BaseModel):
    device_id: str
    timestamp: datetime
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    connection_count: int
    protocol_distribution: Dict[str, int]

class ThreatAlert(BaseModel):
    alert_id: str
    device_id: str
    threat_type: str
    severity: str
    description: str
    timestamp: datetime
    resolved: bool
    confidence_score: float

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# AI Anomaly Detection System
class AISecurityAnalyzer:
    def __init__(self):
        self.baseline_profiles = {}
        self.threat_patterns = {
            'ddos': {'packets_threshold': 10000, 'connections_threshold': 100},
            'data_exfiltration': {'bytes_sent_threshold': 100000000},
            'malware_communication': {'suspicious_ports': [4444, 6666, 8080, 9999]},
            'unusual_traffic': {'deviation_multiplier': 3.0}
        }
    
    def create_device_baseline(self, device_id: str, historical_data: List[NetworkTraffic]):
        """Create baseline profile for normal device behavior"""
        if not historical_data:
            return
        
        total_bytes_sent = sum(data.bytes_sent for data in historical_data)
        total_bytes_received = sum(data.bytes_received for data in historical_data)
        avg_packets_sent = sum(data.packets_sent for data in historical_data) / len(historical_data)
        avg_connections = sum(data.connection_count for data in historical_data) / len(historical_data)
        
        self.baseline_profiles[device_id] = {
            'avg_bytes_sent': total_bytes_sent / len(historical_data),
            'avg_bytes_received': total_bytes_received / len(historical_data),
            'avg_packets_sent': avg_packets_sent,
            'avg_connections': avg_connections,
            'std_bytes_sent': np.std([data.bytes_sent for data in historical_data]),
            'std_packets_sent': np.std([data.packets_sent for data in historical_data])
        }
    
    def detect_anomalies(self, current_traffic: NetworkTraffic) -> List[Dict]:
        """Detect security anomalies using AI analysis"""
        threats = []
        device_id = current_traffic.device_id
        
        # Enhanced threat detection with more realistic triggers
        # Generate random threats for demo purposes (20% chance per device)
        threat_chance = random.random()
        
        if threat_chance < 0.15:  # 15% chance of generating a threat
            # DDoS Attack (5% chance)
            if threat_chance < 0.05:
                threats.append({
                    'type': 'DDoS Attack',
                    'severity': 'CRITICAL',
                    'confidence': round(random.uniform(0.8, 0.95), 2),
                    'description': f'Massive traffic spike detected: {current_traffic.packets_sent} packets/sec from multiple sources'
                })
            
            # Data Exfiltration (3% chance)
            elif threat_chance < 0.08:
                threats.append({
                    'type': 'Data Exfiltration',
                    'severity': 'HIGH',
                    'confidence': round(random.uniform(0.85, 0.98), 2),
                    'description': f'Suspicious data transfer: {current_traffic.bytes_sent} bytes to external endpoint'
                })
            
            # Malware Communication (2% chance)
            elif threat_chance < 0.10:
                threats.append({
                    'type': 'Malware Communication',
                    'severity': 'HIGH',
                    'confidence': round(random.uniform(0.75, 0.90), 2),
                    'description': 'Device communicating with known malicious IP addresses'
                })
            
            # Brute Force Attack (3% chance)
            elif threat_chance < 0.13:
                threats.append({
                    'type': 'Brute Force Attack',
                    'severity': 'MEDIUM',
                    'confidence': round(random.uniform(0.70, 0.85), 2),
                    'description': 'Multiple failed authentication attempts detected'
                })
            
            # Unusual Traffic Pattern (2% chance)
            else:
                threats.append({
                    'type': 'Unusual Traffic Pattern',
                    'severity': 'MEDIUM',
                    'confidence': round(random.uniform(0.65, 0.80), 2),
                    'description': 'Traffic pattern deviates significantly from established baseline'
                })
        
        # Additional random critical alerts (very rare - 1% chance)
        if random.random() < 0.01:
            critical_threats = [
                'Zero-Day Exploit Detected',
                'Firmware Tampering',
                'Network Intrusion',
                'Device Hijacking',
                'Crypto Mining Activity'
            ]
            threats.append({
                'type': random.choice(critical_threats),
                'severity': 'CRITICAL',
                'confidence': round(random.uniform(0.90, 0.99), 2),
                'description': 'Critical security breach detected - immediate action required'
            })
        
        return threats

# Initialize AI analyzer
ai_analyzer = AISecurityAnalyzer()

# Device simulation data
DEVICE_TYPES = ['Industrial Sensor', 'Smart Camera', 'Robot Controller', 'Environmental Monitor', 'Security Gateway']
LOCATIONS = ['Factory Floor A', 'Warehouse B', 'Production Line 1', 'Quality Control', 'Maintenance Bay', 'Server Room']

def convert_objectid_to_str(obj):
    """Convert MongoDB ObjectId to string for JSON serialization"""
    if isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return convert_objectid_to_str(obj.__dict__)
    elif str(type(obj)) == "<class 'bson.objectid.ObjectId'>":
        return str(obj)
    else:
        return obj

async def generate_sample_devices():
    """Generate sample IoT devices for demo"""
    sample_devices = []
    for i in range(20):
        device = {
            "device_id": str(uuid.uuid4()),
            "device_name": f"{random.choice(DEVICE_TYPES)} {i+1:03d}",
            "device_type": random.choice(DEVICE_TYPES),
            "ip_address": f"192.168.{random.randint(1,10)}.{random.randint(1,254)}",
            "mac_address": ':'.join([f"{random.randint(0,255):02x}" for _ in range(6)]),
            "location": random.choice(LOCATIONS),
            "status": random.choice(["online", "offline", "maintenance"]),
            "last_seen": datetime.utcnow() - timedelta(minutes=random.randint(0, 1440)),
            "security_score": round(random.uniform(0.6, 1.0), 2),
            "threat_level": random.choice(["LOW", "MEDIUM", "HIGH"])
        }
        sample_devices.append(device)
    
    # Insert devices if collection is empty
    if await devices_collection.count_documents({}) == 0:
        await devices_collection.insert_many(sample_devices)
        logger.info(f"Inserted {len(sample_devices)} sample devices")

async def simulate_network_traffic():
    """Simulate network traffic data for devices"""
    devices = await devices_collection.find().to_list(length=None)
    
    for device in devices:
        # Generate realistic traffic data
        traffic = NetworkTraffic(
            device_id=device["device_id"],
            timestamp=datetime.utcnow(),
            bytes_sent=random.randint(1000, 50000),
            bytes_received=random.randint(2000, 100000),
            packets_sent=random.randint(100, 5000),
            packets_received=random.randint(200, 10000),
            connection_count=random.randint(1, 20),
            protocol_distribution={
                "https": random.randint(40, 60),
                "mqtt": random.randint(20, 40),
                "tcp": random.randint(10, 30),
                "udp": random.randint(5, 20)
            }
        )
        
        # AI Threat Analysis
        threats = ai_analyzer.detect_anomalies(traffic)
        
        # Store network log
        await network_logs_collection.insert_one(traffic.dict())
        
        # Generate and store threat alerts
        for threat in threats:
            alert = ThreatAlert(
                alert_id=str(uuid.uuid4()),
                device_id=device["device_id"],
                threat_type=threat['type'],
                severity=threat['severity'],
                description=threat['description'],
                timestamp=datetime.utcnow(),
                resolved=False,
                confidence_score=threat['confidence']
            )
            await threats_collection.insert_one(alert.dict())
            
            # Broadcast real-time alert
            await manager.broadcast(json.dumps({
                "type": "threat_alert",
                "data": alert.dict()
            }, default=str))
        
        # Update device security score based on threats
        threat_impact = len(threats) * 0.1
        new_score = max(0.0, device["security_score"] - threat_impact)
        await devices_collection.update_one(
            {"device_id": device["device_id"]},
            {"$set": {"security_score": new_score, "last_seen": datetime.utcnow()}}
        )

# Background task for continuous monitoring
async def monitoring_loop():
    """Background task for continuous network monitoring"""
    while True:
        try:
            await simulate_network_traffic()
            await asyncio.sleep(5)  # Run every 5 seconds for more frequent updates
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            await asyncio.sleep(15)

# API Endpoints
@app.on_event("startup")
async def startup_event():
    await generate_sample_devices()
    # Start monitoring loop
    asyncio.create_task(monitoring_loop())

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/devices")
async def get_devices():
    """Get all IoT devices"""
    devices = await devices_collection.find().to_list(length=None)
    # Convert ObjectId to string for JSON serialization
    devices = convert_objectid_to_str(devices)
    return {"devices": devices}

@app.get("/api/devices/{device_id}")
async def get_device_details(device_id: str):
    """Get detailed information about a specific device"""
    device = await devices_collection.find_one({"device_id": device_id})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get recent network logs
    recent_logs = await network_logs_collection.find(
        {"device_id": device_id}
    ).sort("timestamp", -1).limit(50).to_list(length=None)
    
    # Get recent threats
    recent_threats = await threats_collection.find(
        {"device_id": device_id}
    ).sort("timestamp", -1).limit(20).to_list(length=None)
    
    # Convert ObjectId to string for JSON serialization
    device = convert_objectid_to_str(device)
    recent_logs = convert_objectid_to_str(recent_logs)
    recent_threats = convert_objectid_to_str(recent_threats)
    
    return {
        "device": device,
        "recent_logs": recent_logs,
        "recent_threats": recent_threats
    }

@app.get("/api/threats")
async def get_threats():
    """Get all security threats"""
    threats = await threats_collection.find().sort("timestamp", -1).limit(100).to_list(length=None)
    # Convert ObjectId to string for JSON serialization
    threats = convert_objectid_to_str(threats)
    return {"threats": threats}

@app.get("/api/dashboard")
async def get_dashboard_data():
    """Get dashboard overview data"""
    total_devices = await devices_collection.count_documents({})
    online_devices = await devices_collection.count_documents({"status": "online"})
    offline_devices = await devices_collection.count_documents({"status": "offline"})
    
    # Recent threats (last 24 hours)
    last_24h = datetime.utcnow() - timedelta(hours=24)
    recent_threats = await threats_collection.count_documents({"timestamp": {"$gte": last_24h}})
    
    # Threat severity breakdown
    critical_threats = await threats_collection.count_documents({"severity": "CRITICAL", "resolved": False})
    high_threats = await threats_collection.count_documents({"severity": "HIGH", "resolved": False})
    medium_threats = await threats_collection.count_documents({"severity": "MEDIUM", "resolved": False})
    
    # Average security score
    pipeline = [{"$group": {"_id": None, "avg_score": {"$avg": "$security_score"}}}]
    avg_score_result = await devices_collection.aggregate(pipeline).to_list(length=1)
    avg_security_score = avg_score_result[0]["avg_score"] if avg_score_result else 0.8
    
    return {
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": offline_devices,
        "recent_threats": recent_threats,
        "critical_threats": critical_threats,
        "high_threats": high_threats,
        "medium_threats": medium_threats,
        "avg_security_score": round(avg_security_score, 2),
        "network_status": "monitoring" if online_devices > 0 else "offline"
    }

@app.post("/api/threats/{alert_id}/resolve")
async def resolve_threat(alert_id: str):
    """Mark a threat as resolved"""
    result = await threats_collection.update_one(
        {"alert_id": alert_id},
        {"$set": {"resolved": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Threat not found")
    return {"message": "Threat resolved successfully"}

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            dashboard_data = await get_dashboard_data()
            await websocket.send_text(json.dumps({
                "type": "dashboard_update",
                "data": dashboard_data
            }))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)