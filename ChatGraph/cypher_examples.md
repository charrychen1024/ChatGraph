# Cypher 查询示例（企业知识图谱）

以下是常见的企业知识图谱查询问题及其对应的 Cypher 查询语句，供大模型参考：

---

## 1. 查询某个人投资了哪些公司
- 中文：张伟投资了哪些公司？
- 英文：Which companies has Zhang Wei invested in?
- Cypher：
```cypher
MATCH (p:Person {name: "张伟"})-[:PERSON_INVESTMENT]->(c:Company)
RETURN c.name AS 公司名称, c.credit_code AS 统一社会信用代码
```

---

## 2. 查询某公司法定代表人是谁
- 中文：江苏科技有限公司的法定代表人是谁？
- 英文：Who is the legal representative of Jiangsu Technology Co., Ltd.?
- Cypher：
```cypher
MATCH (p:Person)-[:PER_LEGAL_PERSON]->(c:Company {name: "江苏科技有限公司"})
RETURN p.name AS 法定代表人
```

---

## 3. 查询某公司有哪些分支机构
- 中文：青海省制造集团公司有哪些分支机构？
- 英文：What are the branches of Qinghai Manufacturing Group?
- Cypher：
```cypher
MATCH (parent:Company {name: "青海省制造集团公司"})-[:COM_BRANCH]->(branch:Company)
RETURN branch.name AS 分支机构名称
```

---

## 4. 查询某人担任了哪些公司的法定代表人
- 中文：王强担任了哪些公司的法定代表人？
- 英文：Which companies is Wang Qiang the legal representative of?
- Cypher：
```cypher
MATCH (p:Person {name: "王强"})-[:PER_LEGAL_PERSON]->(c:Company)
RETURN c.name AS 公司名称
```

---

## 5. 查询某人担任了哪些职位
- 中文：他还担任了哪些职位？
- 英文：What other positions does he hold?
- Cypher：
```cypher
MATCH (p:Person {name: "xxx"})-[r:PER_JOB]->(c:Company)
RETURN c.name AS 公司名称, r.job_type AS 职位

# 使用实际的姓名替代xxx
```

---

## 6. 查询某公司所有投资人
- 中文：江苏科技有限公司有哪些投资人？
- 英文：Who are the investors of Jiangsu Technology Co., Ltd.?
- Cypher：
```cypher
MATCH (p:Person)-[:PERSON_INVESTMENT]->(c:Company {name: "江苏科技有限公司"})
RETURN p.name AS 投资人
```

---

## 7. 查询某公司所有董事
- 中文：苏州贸易有限公司的董事有哪些？
- 英文：Who are the directors of Suzhou Trading Co., Ltd.?
- Cypher：
```cypher
MATCH (p:Person)-[r:PER_JOB {job_type: "董事"}]->(c:Company {name: "苏州贸易有限公司"})
RETURN p.name AS 董事姓名
```

---

## 8. 查询某公司所有分公司
- 中文：江苏科技有限公司有哪些分公司？
- 英文：What are the subsidiaries of Jiangsu Technology Co., Ltd.?
- Cypher：
```cypher
MATCH (parent:Company {name: "江苏科技有限公司"})-[:COM_BRANCH]->(branch:Company)
RETURN branch.name AS 分公司名称
```

---

## 9. 查询某公司所有员工
- 中文：江苏科技有限公司有哪些员工？
- 英文：Who are the employees of Jiangsu Technology Co., Ltd.?
- Cypher：
```cypher
MATCH (p:Person)-[:PER_JOB]->(c:Company {name: "江苏科技有限公司"})
RETURN p.name AS 员工姓名, r.job_type AS 职位
```

---

## 10. 查询某公司所有法人
- 中文：江苏科技有限公司的法人有哪些？
- 英文：Who are the legal persons of Jiangsu Technology Co., Ltd.?
- Cypher：
```cypher
MATCH (p:Person)-[:PER_LEGAL_PERSON]->(c:Company {name: "江苏科技有限公司"})
RETURN p.name AS 法人姓名
``` 

## 11. 查询多度以内企业投资关系关联出的公司
- 中文：江苏省制造有限公司三度以内对外的投资关系，一共关联出了哪些公司？
- 英文：Which companies are related to Jiangsu Manufacturing Co., Ltd. through investment relationships within three degrees?
- Cypher:
```
MATCH (c:Company {name: "江苏省制造有限公司"}) -[:COMPANY_INVESTMENT*1..3]-> (m:Company)
RETURN DISTINCT m.name as 公司名称
```
