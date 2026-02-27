"""Seed the database with data from the architect's PDF."""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, create_db_and_tables
from app.models import CostCategory, CostArticle, CostTransaction

create_db_and_tables()
db = SessionLocal()

# Check if already seeded
if db.query(CostCategory).count() > 0:
    print("Database already has data. Skipping seed.")
    db.close()
    sys.exit(0)

# === SEED DATA FROM ARCHITECT PDF ===

# 1. Arquiteto (€6,130.75)
arquiteto = CostCategory(name="Arquiteto", budgeted_total=6130.75)
db.add(arquiteto)
db.flush()

projeto = CostArticle(category_id=arquiteto.id, name="Projeto arquitetura", budgeted_amount=5500.0, notes="Pago em diversas fases")
db.add(projeto)
db.flush()
for phase in range(1, 5):
    db.add(CostTransaction(article_id=projeto.id, transaction_date="2025-01-01", phase_number=phase, payment_method="Dinheiro", amount=1100.0, has_invoice=False))
db.add(CostTransaction(article_id=projeto.id, transaction_date="2025-01-01", phase_number=5, payment_method="Transferência", amount=1100.0, has_invoice=True))

revisao = CostArticle(category_id=arquiteto.id, name="Revisão dos materiais e assistência", budgeted_amount=300.0)
db.add(revisao)
db.flush()
db.add(CostTransaction(article_id=revisao.id, transaction_date="2025-01-01", phase_number=1, payment_method="Transferência", amount=300.0, has_invoice=False))

distico = CostArticle(category_id=arquiteto.id, name="Dístico do Alvará", budgeted_amount=30.75, notes="25 + IVA")
db.add(distico)
db.flush()
db.add(CostTransaction(article_id=distico.id, transaction_date="2025-01-01", phase_number=1, payment_method="MBWay", amount=30.75, has_invoice=False))

# 2. Empreiteiro (€35,530)
empreiteiro = CostCategory(name="Empreiteiro", budgeted_total=35530.0)
db.add(empreiteiro)
db.flush()

assinatura = CostArticle(category_id=empreiteiro.id, name="Assinatura", budgeted_amount=8500.0)
db.add(assinatura)
db.flush()
db.add(CostTransaction(article_id=assinatura.id, transaction_date="2025-01-01", payment_method="Dinheiro", amount=8500.0, has_invoice=False))

fase1 = CostArticle(category_id=empreiteiro.id, name="1ª Fase", budgeted_amount=27030.0)
db.add(fase1)
db.flush()
db.add(CostTransaction(article_id=fase1.id, transaction_date="2025-01-01", phase_number=1, payment_method="Transferência", amount=27030.0, has_invoice=True))

# 3. Electricista (€850)
electricista = CostCategory(name="Electricista", budgeted_total=850.0)
db.add(electricista)
db.flush()

baixada = CostArticle(category_id=electricista.id, name="Baixada", budgeted_amount=850.0, notes="900 + IVA")
db.add(baixada)
db.flush()
db.add(CostTransaction(article_id=baixada.id, transaction_date="2025-01-01", payment_method="Dinheiro", amount=850.0, has_invoice=False))

# 4. Picheleiro (€80)
picheleiro = CostCategory(name="Picheleiro", budgeted_total=80.0)
db.add(picheleiro)
db.flush()

ponto_agua = CostArticle(category_id=picheleiro.id, name="Ponto de Água e ACs", budgeted_amount=80.0)
db.add(ponto_agua)
db.flush()
db.add(CostTransaction(article_id=ponto_agua.id, transaction_date="2025-01-01", phase_number=1, payment_method="MBWay", amount=80.0, has_invoice=False))

# 5. Maquinista (€1,777.22)
maquinista = CostCategory(name="Maquinista", budgeted_total=1777.22)
db.add(maquinista)
db.flush()

giratoria = CostArticle(category_id=maquinista.id, name="Giratória", budgeted_amount=595.0)
db.add(giratoria)
db.flush()
db.add(CostTransaction(article_id=giratoria.id, transaction_date="2025-01-01", payment_method="Dinheiro", amount=595.0, has_invoice=False))

carrinhas = CostArticle(category_id=maquinista.id, name="Carrinhas", budgeted_amount=752.5)
db.add(carrinhas)
db.flush()
db.add(CostTransaction(article_id=carrinhas.id, transaction_date="2025-01-01", payment_method="Dinheiro", amount=752.5, has_invoice=False))

transp = CostArticle(category_id=maquinista.id, name="Transporte Máquinas", budgeted_amount=70.0)
db.add(transp)
db.flush()
db.add(CostTransaction(article_id=transp.id, transaction_date="2025-01-01", payment_method="Dinheiro", amount=70.0, has_invoice=False))

inertes = CostArticle(category_id=maquinista.id, name="Mistura Inertes", budgeted_amount=359.72, notes="DST")
db.add(inertes)
db.flush()
db.add(CostTransaction(article_id=inertes.id, transaction_date="2025-01-01", payment_method="Dinheiro", amount=359.72, has_invoice=True))

# 6. Câmara (€613)
camara = CostCategory(name="Câmara", budgeted_total=613.0)
db.add(camara)
db.flush()

licenca_pedido = CostArticle(category_id=camara.id, name="Licença Ocupação Via Pública - Pedido", budgeted_amount=8.35)
db.add(licenca_pedido)
db.flush()
db.add(CostTransaction(article_id=licenca_pedido.id, transaction_date="2025-01-01", phase_number=1, payment_method="Multibanco", amount=8.35, has_invoice=True))

licenca = CostArticle(category_id=camara.id, name="Licença Ocupação Via Pública - Licença", budgeted_amount=565.4)
db.add(licenca)
db.flush()
db.add(CostTransaction(article_id=licenca.id, transaction_date="2025-01-01", phase_number=1, payment_method="Serviços", amount=565.4, has_invoice=False))

iva_pedido = CostArticle(category_id=camara.id, name="Pedido de IVA a 6% - Pedido", budgeted_amount=26.35)
db.add(iva_pedido)
db.flush()
db.add(CostTransaction(article_id=iva_pedido.id, transaction_date="2025-01-01", phase_number=1, payment_method="Multibanco", amount=26.35, has_invoice=False))

iva_taxa = CostArticle(category_id=camara.id, name="Pedido de IVA a 6% - Taxa", budgeted_amount=12.9)
db.add(iva_taxa)
db.flush()
db.add(CostTransaction(article_id=iva_taxa.id, transaction_date="2025-01-01", phase_number=1, payment_method="Serviços", amount=12.9, has_invoice=False))

db.commit()
print(f"Seeded {db.query(CostCategory).count()} categories, {db.query(CostArticle).count()} articles, {db.query(CostTransaction).count()} transactions")
print(f"Total: €{sum(t.amount for t in db.query(CostTransaction).all()):.2f}")
db.close()
