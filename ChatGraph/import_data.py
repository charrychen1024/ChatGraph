import argparse
from tqdm import tqdm
from data_generator import DataGenerator
from db_connector import Neo4jConnector
import config

def main():
    parser = argparse.ArgumentParser(description='企业关系网络数据生成与导入Neo4j')
    parser.add_argument('--companies', type=int, default=150, help='公司节点数量')
    parser.add_argument('--persons', type=int, default=400, help='人员节点数量')
    parser.add_argument('--clear', action='store_true', help='导入前清空数据库')
    parser.add_argument('--seed', type=int, default=None, help='随机种子')
    args = parser.parse_args()

    print('正在生成数据...')
    dg = DataGenerator(company_num=args.companies, person_num=args.persons, seed=args.seed)
    companies, persons, relationships = dg.generate_all()
    dg.validate()
    print(f'生成公司节点: {len(companies)}，人员节点: {len(persons)}，关系: {len(relationships)}')

    print('正在连接Neo4j...')
    db = Neo4jConnector(config.NEO4J_URI, config.NEO4J_USER, config.NEO4J_PASSWORD, database='neo4j')
    if args.clear:
        print('清空数据库...')
        db.clear_database()

    print('导入公司节点...')
    db.create_companies(companies)
    print('导入人员节点...')
    db.create_persons(persons)
    print('导入关系...')
    db.create_relationships(relationships)
    db.close()
    print('导入完成！')

if __name__ == '__main__':
    main() 