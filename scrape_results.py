from tools.scraper import result_scraper

if __name__ == '__main__':
    rs = result_scraper()
    print(rs.get_results())
