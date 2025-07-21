from neo4j import GraphDatabase

class Neo4jConnector:
    def __init__(self, uri, user, password, database='neo4j'):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session(database=self.database) as session:
            # 删除所有关系
            session.run("MATCH ()-[r]-() DELETE r")
            # 删除所有节点
            session.run("MATCH (n) DELETE n")
            # 验证清空结果
            result = session.run("MATCH (n) RETURN count(n) as count")
            record = result.single()
            count = record['count'] if record else 0
            print(f"数据库清空完成，剩余节点数: {count}")

    def create_companies(self, companies):
        with self.driver.session(database=self.database) as session:
            for company in companies:
                session.run(
                    """
                    CREATE (c:Company {name: $name, credit_code: $credit_code, company_id: $company_id, reg_date: $reg_date, reg_capital: $reg_capital})
                    """,
                    parameters={
                        'name': company['name'],
                        'credit_code': company['credit_code'],
                        'company_id': company['company_id'],
                        'reg_date': company['reg_date'],
                        'reg_capital': company['reg_capital']
                    }
                )

    def create_persons(self, persons):
        with self.driver.session(database=self.database) as session:
            for person in persons:
                session.run(
                    """
                    CREATE (p:Person {name: $name, person_id: $person_id, age: $age, gender: $gender})
                    """,
                    parameters={
                        'name': person['name'],
                        'person_id': person['person_id'],
                        'age': person['age'],
                        'gender': person['gender']
                    }
                )

    def create_relationships(self, relationships):
        with self.driver.session(database=self.database) as session:
            for rel in relationships:
                if rel['type'] == 'company_investment':
                    session.run(
                        """
                        MATCH (a:Company {company_id: $from}), (b:Company {company_id: $to})
                        CREATE (a)-[:COMPANY_INVESTMENT {invest_rate: $invest_rate, invest_date: $invest_date}]->(b)
                        """,
                        parameters={
                            'from': rel['from'],
                            'to': rel['to'],
                            'invest_rate': rel['invest_rate'],
                            'invest_date': rel['invest_date']
                        }
                    )
                elif rel['type'] == 'person_investment':
                    session.run(
                        """
                        MATCH (a:Person {person_id: $from}), (b:Company {company_id: $to})
                        CREATE (a)-[:PERSON_INVESTMENT {invest_rate: $invest_rate, invest_date: $invest_date}]->(b)
                        """,
                        parameters={
                            'from': rel['from'],
                            'to': rel['to'],
                            'invest_rate': rel['invest_rate'],
                            'invest_date': rel['invest_date']
                        }
                    )
                elif rel['type'] == 'com_branch':
                    session.run(
                        """
                        MATCH (a:Company {company_id: $from}), (b:Company {company_id: $to})
                        CREATE (a)-[:COM_BRANCH]->(b)
                        """,
                        parameters={
                            'from': rel['from'],
                            'to': rel['to']
                        }
                    )
                elif rel['type'] == 'per_job':
                    session.run(
                        """
                        MATCH (a:Person {person_id: $from}), (b:Company {company_id: $to})
                        CREATE (a)-[:PER_JOB {job_type: $job_type}]->(b)
                        """,
                        parameters={
                            'from': rel['from'],
                            'to': rel['to'],
                            'job_type': rel['job_type']
                        }
                    )
                elif rel['type'] == 'per_legal_person':
                    session.run(
                        """
                        MATCH (a:Person {person_id: $from}), (b:Company {company_id: $to})
                        CREATE (a)-[:PER_LEGAL_PERSON {job_type: $job_type}]->(b)
                        """,
                        parameters={
                            'from': rel['from'],
                            'to': rel['to'],
                            'job_type': rel['job_type']
                        }
                    ) 