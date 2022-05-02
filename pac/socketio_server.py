import eventlet
import pymysql
import socketio
import json
from pac.local_settings import DATABASES

conn = pymysql.connect(
    host=DATABASES['default']['HOST'],
    user=DATABASES['default']['USER'],
    passwd=DATABASES['default']['PASSWORD'],
    db='mysql')
cur = conn.cursor()
cur.execute("USE db_pac")

sio = socketio.Server(async_mode='eventlet', cors_allowed_origins='*')
app = socketio.WSGIApp(sio)


@sio.on('connect')
def connect(sid, env):
    print('connected ', sid)
    sio.emit('connect', {'id': sid}, room=sid)


@sio.on('init')
def init(sid, data):
    # print('initialization')
    # print("firebase-{}".format(data['id']))
    try:
        # get member
        sio.enter_room(sid, "firebase-{}".format(data['id']))
        cur.execute(
            "SELECT COUNT(*) FROM chats_message WHERE receiver_id = %s and is_read = 0",
            data['id'])
        result = cur.fetchone()
        sio.emit('message_count',
                 {'count': result[0]},
                 room="firebase-{}".format(data['id']))
    except Exception as e:
        # print(e)
        pass


@sio.on('send')
def send(sid, data):
    # print('sending')
    # print(data)
    receiver_id = data['receiver']['id']
    sio.emit('message', data, room="firebase-{}".format(receiver_id))


@sio.on('follow')
def follow(sid, data):
    # print('following')
    followed = data
    sio.emit('followed', {"id": sid}, room="firebase-{}".format(followed))


@sio.on('disconnect')
def disconnect(sid):
    print('disconnected ', sid)

# Other functionalities in the code


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8080)), app)
