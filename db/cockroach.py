from argparse import RawTextHelpFormatter

import psycopg2
import uuid

class crdb:
    def __init__(self, name, timezone, userid=str(uuid.uuid1())):
        print('creating user with name [{}], timezone [{}], userid [{}]'.format(name, timezone, userid))
        self.conn = psycopg2.connect("postgres://andre:BJLHhU_VMm1YumUk@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/skinny-boar-273.defaultdb?sslmode=verify-full&sslrootcert=C:\\Users\\Andre\\Documents\\GitHub\\HackTheNorth2021\\certs\\cc-ca.crt")
        self.name = name;
        self.timezone = timezone;
        self.user_id = userid;
        self.create_user()

    def create_user(self):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO defaultdb.users (user_id, name, timezone) VALUES ('" + self.user_id + "', '" + self.name + "', '" + self.timezone + "') ON CONFLICT DO NOTHING;")
            print("create_user(): status message: %s", cur.statusmessage)
            self.conn.commit()

    def create_group(self, name, timezone):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO defaultdb.groups (name, timezone, members) VALUES ('" + name + "', '" + timezone + "', '{}') ON CONFLICT DO NOTHING;")
            print("create_group(): status message: %s", cur.statusmessage)
            self.conn.commit()

    def get_user_tracking_data(self, userid):
        with self.conn.cursor() as cur:
            cur.execute("SELECT user_id, track_name, track_subname, start_time, end_time FROM defaultdb.public.tracking WHERE user_id = '" + userid + "'")
            print("get_user_tracking_data(): status message: %s", cur.statusmessage)
            rows = cur.fetchall()
            self.conn.commit()
            for row in rows:
                print(row)

    def get_group_tracking_data(self, name, exclude_user=False):
        with self.conn.cursor() as cur:
            cur.execute("SELECT users.user_id, users.name, tracking.track_name, tracking.track_subname, tracking.start_time, tracking.end_time FROM defaultdb.public.groups INNER JOIN defaultdb.public.users ON users.user_id = ANY (groups.members) INNER JOIN defaultdb.public.tracking ON tracking.user_id = users.user_id WHERE groups.name = '" + name + "'"
                        + (" AND users.user_id!='" + self.user_id + "'" if exclude_user else ""))
            print("get_group_tracking_data(): status message: %s", cur.statusmessage)
            rows = cur.fetchall()
            self.conn.commit()
            for row in rows:
                print(row)

    def add_to_group(self, groupid, userid):
        self.remove_from_group(groupid, userid)
        with self.conn.cursor() as cur:
            cur.execute("UPDATE groups SET members = array_append(members, '" + userid + "') WHERE name = '" + groupid + "';")
            print("add_to_group(): status message: %s", cur.statusmessage)
            self.conn.commit()

    def remove_from_group(self, groupid, userid):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE groups SET members = array_remove(members, '" + userid + "') WHERE name = '" + groupid + "';")
            print("remove_from_group(): status message: %s", cur.statusmessage)
            self.conn.commit()

    def add_tracking_data(self, track_name, track_subname, start_time, end_time):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO defaultdb.tracking (user_id, track_name, track_subname, start_time, end_time) VALUES ('"
                + self.user_id + "', '" + track_name + "', '" + track_subname + "', '" + str(start_time) + "', '" + str(end_time) + "') ON CONFLICT DO NOTHING;")
            print("create_group(): status message: %s", cur.statusmessage)
            self.conn.commit()

    # self.conn.close()?

db = crdb("baobei", "CHINA", 'dc8448c4-583c-11eb-a227-8c8caa42b62e')
db.create_group('Tianjin Students', 'CHINA')
db.get_user_tracking_data('bd4e02d4-583c-11eb-ae93-0242ac130002')
db.get_group_tracking_data('Tianjin Students')
db.get_group_tracking_data('Tianjin Students', True)
# db.remove_from_group('Tianjin Students', db.user_id)
db.add_to_group('Tianjin Students', db.user_id)
db.add_tracking_data("test name", 'test subname', 1, 2)