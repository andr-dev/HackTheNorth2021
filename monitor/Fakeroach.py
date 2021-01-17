import uuid


class CRDB:
    def __init__(self, name, timezone, userid=str(uuid.uuid1())):
        print('creating user with name [{}], timezone [{}], userid [{}]'.format(name, timezone, userid))
        self.name = name;
        self.timezone = timezone;
        self.user_id = userid;
        self.create_user()

    def create_user(self):
        print('create_user')

    def create_group(self, name, timezone):
        print('create_group')

    def get_user_tracking_data(self, userid):
        return []

    def get_group_tracking_data(self, name, exclude_user=False):
        return []

    def add_to_group(self, groupid, userid):
        print('added to group')

    def join_group(self, groupid):
        self.add_to_group(groupid, self.user_id)

    def remove_from_group(self, groupid, userid):
        print('remove from group')

    def leave_group(self, groupid):
        self.remove_from_group(groupid, self.user_id)

    def add_tracking_data(self, track_name, track_process, start_time, end_time):
        print('add tracking data')

    def get_members_in_group(self, groupid):
        return []

    def get_user_groups(self):
        return []

    def get_group_timezone(self, name):
        return "EST"