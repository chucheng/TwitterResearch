import user_groups

from constants import _USER_INFO_FILE_ID_INDEX
from constants import _USER_INFO_FILE_FOLLOWERS_COUNT_INDEX

def run():

  groups = user_groups.get_all_user_groups()

  sum_num_followers_experts = 0
  sum_num_followers_common = 0
  sum_num_followers_other = 0

  num_experts = 0
  num_common = 0
  num_other = 0

  with open("../data/SocialHubBias/user_info.tsv") as in_file:
    for line in in_file:
      tokens = line.split("\t")
      user_id = tokens[_USER_INFO_FILE_ID_INDEX].strip()
      num_followers = int(tokens[_USER_INFO_FILE_FOLLOWERS_COUNT_INDEX].strip())
      if user_id in groups.all_experts:
        sum_num_followers_experts += num_followers
        num_experts += 1
      elif user_id in groups.common_users:
        sum_num_followers_common += num_followers
        num_common += 1
      else:
        sum_num_followers_other += num_followers
        num_other += 1

  with open("../data/SocialHubBias/avg_num_followers.tsv", 'w') as out_file:
    out_file.write('experts\t%s\n' % (sum_num_followers_experts / num_experts))
    out_file.write('common\t%s\n' % (sum_num_followers_common / num_common))
    out_file.write('other\t%s\n' % (sum_num_followers_other / num_other))


if __name__ == "__main__":
  run()
