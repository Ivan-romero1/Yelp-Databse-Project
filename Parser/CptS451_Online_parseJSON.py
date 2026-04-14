import json


def cleanStr4SQL(s):
    return s.replace("'","''").replace("\n"," ")

def cleanStr4CSV(s):
    return str(s).replace('"', '""').replace("\n", " ")

def getAttributes(attributes):
    L = []
    for (attribute, value) in list(attributes.items()):
        if isinstance(value, dict):
            L += getAttributes(value)
        else:
            L.append((attribute,value))
    return L

def parseBusinessData():
    print("Parsing businesses...")
    # read the JSON file
    with open('./yelp_business.JSON', 'r') as f:
        outfile = open('./yelp_business.txt', 'w', encoding='utf-8')    # encoding ensures no errors interpreting characters
        categoriesOutfile = open('./yelp_business_categories.txt', 'w', encoding='utf-8')
        hoursOutfile = open('./yelp_business_hours.txt', 'w', encoding='utf-8')
        attributesOutfile = open('./yelp_business_attributes.txt', 'w', encoding='utf-8')

        line = f.readline()
        count_line = 0

        # read each JSON object and extract data
        while line:
            data = json.loads(line)
            business = data['business_id']  # business id

            business_str = '"' + cleanStr4CSV(business) + '",' + \
                           '"' + cleanStr4CSV(data['name']) + '",' + \
                           '"' + cleanStr4CSV(data['address']) + '",' + \
                           '"' + cleanStr4CSV(data['city']) + '",' + \
                           '"' + cleanStr4CSV(data['state']) + '",' + \
                           '"' + cleanStr4CSV(data['postal_code']) + '",' + \
                           str(data['latitude']) + ',' + \
                           str(data['longitude']) + ',' + \
                           str(data['stars']) + ',' + \
                           str(data['review_count']) + ',' + \
                           str(data['is_open'])
            outfile.write(business_str + '\n')

            # process business categories
            if data['categories'] is not None:
                for category in data['categories']:
                    category_str = '"' + cleanStr4CSV(business) + '",' + \
                                   '"' + cleanStr4CSV(category) + '"'
                    categoriesOutfile.write(category_str + '\n')

            # process business hours
            if data['hours'] is not None:
                for (day, hours) in data['hours'].items():
                    hours_str = '"' + cleanStr4CSV(business) + '",' + \
                                '"' + cleanStr4CSV(day) + '",' + \
                                '"' + cleanStr4CSV(hours.split('-')[0]) + '",' + \
                                '"' + cleanStr4CSV(hours.split('-')[1]) + '"'
                    hoursOutfile.write(hours_str + '\n')

            # process business attributes
            if data['attributes'] is not None:
                for (attr, value) in getAttributes(data['attributes']):
                    attr_str = '"' + cleanStr4CSV(business) + '",' + \
                               '"' + cleanStr4CSV(attr) + '",' + \
                               '"' + cleanStr4CSV(value) + '"'
                    attributesOutfile.write(attr_str + '\n')

            line = f.readline()
            count_line += 1

        print(count_line)

        outfile.close()
        categoriesOutfile.close()
        hoursOutfile.close()
        attributesOutfile.close()

def parseCheckInData():
    print("Parsing checkins...")
    with open('./yelp_checkin.JSON', 'r') as f:
        outfile = open('./yelp_checkin.txt', 'w', encoding='utf-8')
        line = f.readline()
        count_line = 0

        while line:
            data = json.loads(line)
            business = data['business_id']

            if data['time'] is not None:
                for day, times in data['time'].items():
                    for hour, count in times.items():
                        checkin_str = '"' + cleanStr4CSV(business) + '",' + \
                                      '"' + cleanStr4CSV(day) + '",' + \
                                      '"' + cleanStr4CSV(hour) + '",' + \
                                      str(count)
                        outfile.write(checkin_str + '\n')

            line = f.readline()
            count_line += 1

        print(count_line)
        outfile.close()

def parseReviewData():
    print("Parsing reviews...")
    with open('./yelp_review.JSON', 'r') as f:
        outfile = open('./yelp_review.txt', 'w', encoding='utf-8')
        line = f.readline()
        count_line = 0

        while line:
            data = json.loads(line)

            review_str = '"' + cleanStr4CSV(data['business_id']) + '",' + \
                         '"' + cleanStr4CSV(data['user_id']) + '",' + \
                         '"' + cleanStr4CSV(data['review_id']) + '",' + \
                         str(data['stars']) + ',' + \
                         '"' + cleanStr4CSV(data['date']) + '",' + \
                         '"' + cleanStr4CSV(data['text']) + '",' + \
                         str(data['useful']) + ',' + \
                         str(data['funny']) + ',' + \
                         str(data['cool'])

            outfile.write(review_str + '\n')

            line = f.readline()
            count_line += 1

        print(count_line)
        outfile.close()

def parseUserData():
    print("Parsing users...")
    with open('./yelp_user.JSON', 'r') as f:
        outfile = open('./yelp_user.txt', 'w', encoding='utf-8')
        eliteOutfile = open('./yelp_user_elite.txt', 'w', encoding='utf-8')
        friendsOutfile = open('./yelp_user_friends.txt', 'w', encoding='utf-8')

        line = f.readline()
        count_line = 0

        while line:
            data = json.loads(line)
            user = data['user_id']

            user_str = '"' + cleanStr4CSV(user) + '",' + \
                       '"' + cleanStr4CSV(data['name']) + '",' + \
                       str(data['review_count']) + ',' + \
                       str(data['useful']) + ',' + \
                       str(data['funny']) + ',' + \
                       str(data['cool']) + ',' + \
                       str(data['fans']) + ',' + \
                       str(data['average_stars']) + ',' + \
                       '"' + cleanStr4CSV(data['yelping_since']) + '",' + \
                       str(data['compliment_cool']) + ',' + \
                       str(data['compliment_cute']) + ',' + \
                       str(data['compliment_funny']) + ',' + \
                       str(data['compliment_hot']) + ',' + \
                       str(data['compliment_list']) + ',' + \
                       str(data['compliment_more']) + ',' + \
                       str(data['compliment_note']) + ',' + \
                       str(data['compliment_photos']) + ',' + \
                       str(data['compliment_plain']) + ',' + \
                       str(data['compliment_profile']) + ',' + \
                       str(data['compliment_writer'])

            outfile.write(user_str + '\n')

            if data['elite'] is not None:
                for year in data['elite']:
                    elite_str = '"' + cleanStr4CSV(user) + '",' + \
                                '"' + cleanStr4CSV(year) + '"'
                    eliteOutfile.write(elite_str + '\n')

            if data['friends'] is not None:
                for friend in data['friends']:
                    friend_str = '"' + cleanStr4CSV(user) + '",' + \
                                 '"' + cleanStr4CSV(friend) + '"'
                    friendsOutfile.write(friend_str + '\n')

            line = f.readline()
            count_line += 1

        print(count_line)
        outfile.close()
        eliteOutfile.close()
        friendsOutfile.close()


parseBusinessData()
parseCheckInData()
parseReviewData()
parseUserData()
