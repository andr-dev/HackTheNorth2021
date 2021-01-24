from argparse import RawTextHelpFormatter

import psycopg2
import uuid


class CRDB:
    def __init__(self, name, timezone, userid=str(uuid.uuid1())):
        print('creating user with name [{}], timezone [{}], userid [{}]'.format(name, timezone, userid))
        #self.conn = psycopg2.connect("postgres://andre:BJLHhU_VMm1YumUk@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/skinny-boar-273.defaultdb?sslmode=verify-full&sslrootcert=C:\\Users\\Andre\\Documents\\GitHub\\HackTheNorth2021\\certs\\cc-ca.crt")
        self.conn = psycopg2.connect("postgres://user:password1234@trusty-lemur-8c3.gcp-northamerica-northeast1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&sslrootcert=C:\\Users\\Andre\\Documents\\GitHub\\HackTheNorth2021\\certs\\trusty-lemur-ca.crt")
        self.name = name
        self.timezone = timezone
        self.user_id = userid
        self.create_user()

    def create_user(self):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO defaultdb.andr_users (user_id, name, timezone) VALUES ('" + self.user_id + "', '" + self.name + "', '" + self.timezone + "') ON CONFLICT DO NOTHING;")
            print("create_user(): status message: %s", cur.statusmessage)
            self.conn.commit()

    def create_group(self, name, timezone):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO defaultdb.andr_groups (name, timezone, members) VALUES ('" + name + "', '" + timezone + "', '{}') ON CONFLICT DO NOTHING;")
            print("create_group(): status message: %s", cur.statusmessage)
            self.conn.commit()

    def get_user_tracking_data(self, userid):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, track_name, track_process, start_time, end_time FROM defaultdb.public.andr_tracking WHERE user_id = '" + userid + "'")
            print("get_user_tracking_data(): status message: %s", cur.statusmessage)
            rows = cur.fetchall()
            self.conn.commit()
            for row in rows:
                print(row)
            return rows

    def get_group_tracking_data(self, name, exclude_user=False):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT andr_users.user_id, andr_users.name, andr_tracking.track_name, andr_tracking.track_process, andr_tracking.start_time, andr_tracking.end_time FROM defaultdb.public.andr_groups INNER JOIN defaultdb.public.andr_users ON andr_users.user_id = ANY (andr_groups.members) INNER JOIN defaultdb.public.andr_tracking ON andr_tracking.user_id = andr_users.user_id WHERE andr_groups.name = '" + name + "'"
                + (" AND andr_users.user_id!='" + self.user_id + "'" if exclude_user else ""))
            print("get_group_tracking_data(): status message: %s", cur.statusmessage)
            rows = cur.fetchall()
            self.conn.commit()
            return rows

    def add_to_group(self, groupid, userid):
        self.remove_from_group(groupid, userid)
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE andr_groups SET members = array_append(members, '" + userid + "') WHERE name = '" + groupid + "';")
            print("add_to_group(): status message: %s", cur.statusmessage)
            self.conn.commit()

    def join_group(self, groupid):
        self.add_to_group(groupid, self.user_id)

    def remove_from_group(self, groupid, userid):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE andr_groups SET members = array_remove(members, '" + userid + "') WHERE name = '" + groupid + "';")
            print("remove_from_group(): status message: %s", cur.statusmessage)
            self.conn.commit()

    def leave_group(self, groupid):
        self.remove_from_group(groupid, self.user_id)

    def add_tracking_data(self, track_name, track_process, start_time, end_time):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO defaultdb.andr_tracking (user_id, track_name, track_process, start_time, end_time) VALUES ('"
                + self.user_id + "', '" + track_name + "', '" + track_process + "', '" + str(start_time) + "', '" + str(
                    end_time) + "') ON CONFLICT DO NOTHING;")
            print("create_group(): status message: %s", cur.statusmessage)
            self.conn.commit()

    def get_members_in_group(self, groupid):
        with self.conn.cursor() as cur:
            cur.execute("SELECT andr_users.name FROM andr_groups INNER JOIN andr_users ON andr_users.user_id = ANY (andr_groups.members) WHERE andr_groups.name = '" + groupid + "';")
            print("get_members_in_group(): status message: %s", cur.statusmessage)
            rows = cur.fetchall()
            self.conn.commit()
            out = []
            for row in rows:
                out.append(row[0])
            return out

    def get_user_groups(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT andr_groups.name FROM andr_groups WHERE '" + self.user_id + "'::UUID = ANY (andr_groups.members);")
            print("get_members_in_group(): status message: %s", cur.statusmessage)
            rows = cur.fetchall()
            self.conn.commit()
            out = []
            for row in rows:
                out.append(row[0])
            return out

    def get_group_timezone(self, name):
        with self.conn.cursor() as cur:
            cur.execute("SELECT andr_groups.timezone FROM andr_groups WHERE andr_groups.name='" + name + "'")
            print("get_members_in_group(): status message: %s", cur.statusmessage)
            rows = cur.fetchall()
            self.conn.commit()
            return rows[0][0]

    def get_users(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT andr_users.user_id, andr_users.name FROM andr_users")
            self.conn.commit()



    # self.conn.close()?

db = CRDB("anzhui", "EST", 'dc8448c4-583c-11eb-a227-8c8caa42b62e')
# db.create_group('Tianjin Students', 'CHINA')
# db.get_user_tracking_data('bd4e02d4-583c-11eb-ae93-0242ac130002')
# db.get_group_tracking_data('Tianjin Students')
# db.get_group_tracking_data('Tianjin Students', True)
# db.remove_from_group('Tianjin Students', db.user_id)
# db.add_to_group('Tianjin Students', db.user_id)
# db.add_tracking_data("test name", 'test subname', 1, 2)
# db.get_members_in_group('Tianjin Students')
# print(db.get_user_tracking_data('dc8448c4-583c-11eb-a227-8c8caa42b62e'))
print(print(db.get_group_tracking_data('test 2')))