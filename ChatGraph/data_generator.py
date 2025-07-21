from faker import Faker
import random
from datetime import datetime, timedelta

class DataGenerator:
    def __init__(self, company_num=150, person_num=400, seed=None):
        self.fake = Faker('zh_CN')
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        self.company_num = company_num
        self.person_num = person_num
        self.companies = []
        self.persons = []
        self.relationships = []
        self.company_id_set = set()
        self.person_id_set = set()
        self.credit_code_set = set()

    def _generate_credit_code(self):
        # 18位，数字和大写字母
        while True:
            code = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=18))
            if code not in self.credit_code_set:
                self.credit_code_set.add(code)
                return code

    def generate_company(self):
        area = self.fake.province()
        industry = random.choice(['科技', '贸易', '制造', '投资', '咨询', '地产', '医药', '教育'])
        org_type = random.choice(['有限公司', '股份公司', '集团公司', '合伙企业'])
        name = f"{area}{industry}{org_type}"
        credit_code = self._generate_credit_code()
        company_id = len(self.companies) + 1
        reg_date = self.fake.date_between(start_date='-23y', end_date='today').strftime('%Y-%m-%d')
        reg_capital = round(random.uniform(10, 10000), 2)
        company = {
            'name': name,
            'credit_code': credit_code,
            'company_id': company_id,
            'reg_date': reg_date,
            'reg_capital': reg_capital
        }
        self.companies.append(company)
        self.company_id_set.add(company_id)
        return company

    def generate_person(self):
        name = self.fake.name()
        person_id = len(self.persons) + 1
        age = random.randint(18, 70)
        gender = random.choice(['男', '女'])
        person = {
            'name': name,
            'person_id': person_id,
            'age': age,
            'gender': gender
        }
        self.persons.append(person)
        self.person_id_set.add(person_id)
        return person

    def generate_nodes(self):
        for _ in range(self.company_num):
            self.generate_company()
        for _ in range(self.person_num):
            self.generate_person()

    def generate_relationships(self):
        # 1. 企业投资关系(company_investment)
        for company in self.companies:
            n = random.randint(1, 3)
            for _ in range(n):
                # 随机选择另一个公司作为被投资对象
                target = random.choice(self.companies)
                if target['company_id'] == company['company_id']:
                    continue
                rel = {
                    'type': 'company_investment',
                    'from': company['company_id'],
                    'to': target['company_id'],
                    'invest_rate': round(random.uniform(0.01, 1.0), 2),
                    'invest_date': self.fake.date_between(start_date='-20y', end_date='today').strftime('%Y-%m-%d')
                }
                self.relationships.append(rel)
            # 人员投资关系
            if random.random() < 0.5:
                person = random.choice(self.persons)
                rel = {
                    'type': 'person_investment',
                    'from': person['person_id'],
                    'to': company['company_id'],
                    'invest_rate': round(random.uniform(0.01, 1.0), 2),
                    'invest_date': self.fake.date_between(start_date='-20y', end_date='today').strftime('%Y-%m-%d')
                }
                self.relationships.append(rel)
        # 2. 分支机构关系(com_branch)
        branch_num = int(len(self.companies) * 0.3)
        branch_companies = random.sample(self.companies, branch_num)
        for company in branch_companies:
            # 随机选择一个母公司
            parent = random.choice(self.companies)
            if parent['company_id'] == company['company_id']:
                continue
            rel = {
                'type': 'com_branch',
                'from': parent['company_id'],
                'to': company['company_id']
            }
            self.relationships.append(rel)
        # 3. 任职关系(per_job)
        job_types = ['董事长', '总经理', '高管', '监事', '财务负责人']
        for company in self.companies:
            n = random.randint(1, 5)
            persons = random.sample(self.persons, n)
            for i, person in enumerate(persons):
                rel = {
                    'type': 'per_job',
                    'from': person['person_id'],
                    'to': company['company_id'],
                    'job_type': random.choice(job_types)
                }
                self.relationships.append(rel)
        # 4. 法人关系(per_legal_person)
        for company in self.companies:
            person = random.choice(self.persons)
            rel = {
                'type': 'per_legal_person',
                'from': person['person_id'],
                'to': company['company_id'],
                'job_type': '法定代表人'
            }
            self.relationships.append(rel)

    def generate_all(self):
        self.generate_nodes()
        self.generate_relationships()
        return self.companies, self.persons, self.relationships

    def validate(self):
        # 可扩展：校验数据合理性
        assert len(self.companies) == self.company_num
        assert len(self.persons) == self.person_num
        # 其他校验可根据需要添加 