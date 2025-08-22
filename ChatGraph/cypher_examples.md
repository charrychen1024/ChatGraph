##  查询某个人投资了哪些公司
- 中文：张伟投资了哪些公司？
- 英文：Which companies has Zhang Wei invested in?
- Cypher：
```cypher
MATCH (p:Person {name: "张伟"})-[:PERSON_INVESTMENT]->(c:Company)
RETURN c.name AS 公司名称, c.credit_code AS 统一社会信用代码
```

##  查询某公司法定代表人是谁
- 中文：江苏科技有限公司的法定代表人是谁？
- 英文：Who is the legal representative of Jiangsu Technology Co., Ltd.?
- Cypher：
```cypher
MATCH (p:Person)-[:PER_LEGAL_PERSON]->(c:Company {name: "江苏科技有限公司"})
RETURN p.name AS 法定代表人
```

## 查询某公司有哪些分支机构
- 中文：青海省制造集团公司有哪些分支机构？
- 英文：What are the branches of Qinghai Manufacturing Group?
- Cypher：
```cypher
MATCH (parent:Company {name: "青海省制造集团公司"})-[:COM_BRANCH]->(branch:Company)
RETURN branch.name AS 分支机构名称
```

## 查询某人担任了哪些公司的法定代表人
- 中文：王强担任了哪些公司的法定代表人？
- 英文：Which companies is Wang Qiang the legal representative of?
- Cypher：
```cypher
MATCH (p:Person {name: "王强"})-[:PER_LEGAL_PERSON]->(c:Company)
RETURN c.name AS 公司名称
```

## 查询某人担任了哪些职位
- 中文：他还担任了哪些职位？
- 英文：What other positions does he hold?
- Cypher：
```cypher
MATCH (p:Person {name: "xxx"})-[r:PER_JOB]->(c:Company)
RETURN c.name AS 公司名称, r.job_type AS 职位

# 使用实际的姓名替代xxx
```

## 查询某公司所有投资人
- 中文：江苏科技有限公司有哪些投资人？
- 英文：Who are the investors of Jiangsu Technology Co., Ltd.?
- Cypher：
```cypher
MATCH (p:Person)-[:PERSON_INVESTMENT]->(c:Company {name: "江苏科技有限公司"})
RETURN p.name AS 投资人
```

## 查询某公司所有董事
- 中文：苏州贸易有限公司的董事有哪些？
- 英文：Who are the directors of Suzhou Trading Co., Ltd.?
- Cypher：
```cypher
MATCH (p:Person)-[r:PER_JOB {job_type: "董事"}]->(c:Company {name: "苏州贸易有限公司"})
RETURN p.name AS 董事姓名
```


## 查询某公司所有分公司
- 中文：江苏科技有限公司有哪些分公司？
- 英文：What are the subsidiaries of Jiangsu Technology Co., Ltd.?
- Cypher：
```cypher
MATCH (parent:Company {name: "江苏科技有限公司"})-[:COM_BRANCH]->(branch:Company)
RETURN branch.name AS 分公司名称
```


## 查询某公司所有员工
- 中文：江苏科技有限公司有哪些员工？
- 英文：Who are the employees of Jiangsu Technology Co., Ltd.?
- Cypher：
```cypher
MATCH (p:Person)-[:PER_JOB]->(c:Company {name: "江苏科技有限公司"})
RETURN p.name AS 员工姓名, r.job_type AS 职位
```

## 查询某公司所有法人
- 中文：江苏科技有限公司的法人有哪些？
- 英文：Who are the legal persons of Jiangsu Technology Co., Ltd.?
- Cypher：
```cypher
MATCH (p:Person)-[:PER_LEGAL_PERSON]->(c:Company {name: "江苏科技有限公司"})
RETURN p.name AS 法人姓名
``` 

## 查询多度以内企业投资关系关联出的公司
- 中文：江苏省制造有限公司三度以内对外的投资关系，一共关联出了哪些公司？
- 英文：Which companies are related to Jiangsu Manufacturing Co., Ltd. through investment relationships within three degrees?
- Cypher:
```
MATCH (c:Company {name: "江苏省制造有限公司"}) -[:COMPANY_INVESTMENT*1..3]-> (m:Company)
RETURN DISTINCT m.name as 公司名称
```

### 查询某家公司指定关系类型多度关联的公司，并且返回路径
#### 示例 1: 查询高管任职关联
  - **中文**: 查询和“阿里巴巴（中国）有限公司”在三度以内，通过“高管任职”关系可以关联到哪些公司？并给出完整的关联路径。
  - **英文**: Which companies are connected to "Alibaba (China) Co., Ltd." within three degrees through the "PER_JOB" relationship? Please provide the complete paths.
  - **Cypher**:
```
MATCH p = (c:Company {name: "阿里巴巴（中国）有限公司"}) -[:PER_JOB*1..3]- (m:Company)
RETURN p
```

#### 示例 1: 查询企业对外投资关联（返回路径）

  - **中文**: 查询“腾讯控股有限公司”在两度以内，通过对外投资关系，关联到了哪些公司？请展示出具体的投资路径。
  - **英文**: Which companies are related to "Tencent Holdings Limited" through investment relationships within two degrees? Please show the specific investment paths.
  - **Cypher**:
```
MATCH p = (c:Company {name: "腾讯控股有限公司"}) -[:COMPANY_INVESTMENT*1..2]-> (m:Company)
RETURN p
```

### 给定一对公司，查询他们之间3度以内是否存在关系，如果有则输出所有的完整的关联关系
#### 示例1: 查询两家公司间的综合关联
  - **中文**: 查询“小米科技有限责任公司”和“上海蔚来汽车有限公司”之间，在三度以内是否存在任何关联关系？如果存在，请展示出所有类型的关联路径。
  - **英文**: Are there any relationships within three degrees between "Xiaomi Technology Co., Ltd." and "Shanghai NIO Automobile Co., Ltd."? If so, please display all types of connection paths.
  - **Cypher**:
```
MATCH p = (c1:Company {name: "小米科技有限责任公司"}) -[*1..3]- (c2:Company {name: "上海蔚来汽车有限公司"})
RETURN p
```

#### 示例2: 查询两家公司间的特定关联（如企业投资关系或分支机构）
  - **中文**: “华为技术有限公司”和“中芯国际集成电路制造有限公司”在三度以内，是否通过共同的股东或者高管产生关联？请列出所有此类关联路径。
  - **英文**: Are "Huawei Technologies Co., Ltd." and "SMIC" connected within three degrees through common shareholders or PER_JOBs? Please list all such connection paths.
  - **Cypher**:
```
MATCH p = (c1:Company {name: "华为技术有限公司"}) -[:COMPANY_INVESTMENT|COM_BRANCH*1..3]- (c2:Company {name: "中芯国际集成电路制造有限公司"})
RETURN p
```

### 给出一个公司list，查询他们两两之间是否有关系，同时给出完整的关联关系
#### 示例: 查询多家公司两两之间的所有关联
  - **中文**: 给定公司列表["百度在线网络技术（北京）有限公司", "北京字节跳动科技有限公司", "美团股份有限公司"]，查询它们两两之间在三度以内的所有关联关系路径。
  - **英文**: Given the company list ["Baidu Online Network Technology (Beijing) Co., Ltd.", "Beijing ByteDance Technology Co., Ltd.", "Meituan Co., Ltd."], find all relationship paths within three degrees between any two of them.
  - **Cypher**:
```
MATCH (c1:Company), (c2:Company)
WHERE c1.name IN ["百度在线网络技术（北京）有限公司", "北京字节跳动科技有限公司", "美团股份有限公司"]
AND c2.name IN ["百度在线网络技术（北京）有限公司", "北京字节跳动科技有限公司", "美团股份有限公司"]
AND id(c1) < id(c2)
MATCH p = (c1)-[*1..3]-(c2)
RETURN p
```


#### 查询共同股东
  - **中文**: 有哪些公司类型或自然人类型的股东同时投资了“A公司”和“B公司”？
  - **英文**: Which shareholders have invested in both "Company A" and "Company B"?
  - **Cypher**:
```
MATCH (p:Person|Company) -[:COMPANY_INVESTMENT|PERSON_INVESTMENT]-> (c1:Company {name: "A公司"})
MATCH (p) -[:COMPANY_INVESTMENT|PERSON_INVESTMENT]-> (c2:Company {name: "B公司"})
RETURN p.name as 共同股东
```

#### 查询人员的商业版图

  - **中文**: 查询“张三”这个人在哪些公司担任法人，在哪些公司担任高管，又投资了哪些公司？
  - **英文**: In which companies does "Zhang San" serve as the legal representative, in which companies as an PER_JOB, and which companies has he invested in?
  - **Cypher**:

```
MATCH (p:Person {name: "张三"})
OPTIONAL MATCH (p) -[:PER_LEGAL_PERSON]-> (c1:Company)
OPTIONAL MATCH (p) -[:PER_JOB]-> (c2:Company)
OPTIONAL MATCH (p) -[:PERSON_INVESTMENT]-> (c3:Company)
RETURN p.name as 姓名, collect(DISTINCT c1.name) as 担任法人的公司, collect(DISTINCT c2.name) as 担任高管的公司, collect(DISTINCT c3.name) as 投资的公司
```

#### 查询企业最终受益人（UBO）

  - **中文**: 向上追溯“某某科技有限公司”的股权结构，找出持股比例超过25%的最终自然人股东。
  - **英文**: Trace the equity structure of "XX Technology Co., Ltd." upwards to find the ultimate beneficial owners (natural person shareholders) with a shareholding ratio exceeding 25%.
  - **Cypher**:
```
MATCH p = (person:Person) <-[:PERSON_INVESTMENT|COMPANY_INVESTMENT*1..5]- (company:Company {name: "某某科技有限公司"})
WHERE ALL(r in relationships(p) where r.invest_rate > 0.1)
RETURN person.name, p
```

*注：此查询需要 `PERSON_INVESTMENT`和`COMPANY_INVESTMENT` 关系上具有 `invest_rate`（持股比例）属性。*

#### 识别集团派系公司

  - **中文**: 查询由“中国平安保险（集团）股份有限公司”通过多层投资最终控制的所有公司（最高限制3度以内）。
  - **英文**: Find all companies ultimately controlled by "Ping An Insurance (Group) Company of China, Ltd." through multiple layers of investment.
  - **Cypher**:
```
MATCH (c:Company {name: "中国平安保险（集团）股份有限公司"}) -[:COMPANY_INVESTMENT*1..3]-> (m:Company)
RETURN DISTINCT m.name as 集团内公司
```

#### 查询人员在多家公司的任职情况
  - **中文**: 查询同时在“A公司”和“B公司”担任高管的人员。
  - **英文**: Find the individuals who are PER_JOBs at both "Company A" and "Company B".
  - **Cypher**:
```
MATCH (c1:Company {name: "A公司"}) <-[:PER_JOB]- (p:Person) -[:PER_JOB]-> (c2:Company {name: "B公司"})
RETURN p.name as 共同高管
```
