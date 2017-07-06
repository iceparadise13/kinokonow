from datetime import datetime, timedelta
import pymongo
import words


if __name__ == '__main__':
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.get_database('kinokonow')
    frequencies = words.get_filtered_noun_frequencies(
        db.nouns, datetime.utcnow() - timedelta(hours=1), words.read_black_list())
    words.print_frequencies(frequencies)
    img = words.generate_word_cloud(frequencies, font_path='font.ttf')
    img.save('out.png')
