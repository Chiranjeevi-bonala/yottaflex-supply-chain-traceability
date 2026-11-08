"""001_initial_schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-11-07 23:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. suppliers
    op.create_table(
        'suppliers',
        sa.Column('supplier_id', sa.String(20), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('country', sa.String(100), nullable=False),
        sa.Column('category', sa.String(30), nullable=False),
        sa.Column('contact_email', sa.String(200), nullable=False),
        sa.Column('contact_phone', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('reliability_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 2. products
    op.create_table(
        'products',
        sa.Column('product_id', sa.String(20), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('sku', sa.String(50), nullable=False, unique=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('uom', sa.String(10), nullable=False),
        sa.Column('shelf_life_days', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 3. bom_items
    op.create_table(
        'bom_items',
        sa.Column('bom_id', sa.String(20), primary_key=True),
        sa.Column('product_id', sa.String(20), sa.ForeignKey('products.product_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('material_type', sa.String(100), nullable=False),
        sa.Column('quantity_per_unit', sa.Numeric(12, 4), nullable=False),
        sa.Column('unit', sa.String(20), nullable=False, server_default='KG'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 4. material_lots
    op.create_table(
        'material_lots',
        sa.Column('lot_id', sa.String(60), primary_key=True),
        sa.Column('supplier_id', sa.String(20), sa.ForeignKey('suppliers.supplier_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('material_type', sa.String(100), nullable=False),
        sa.Column('quantity_kg', sa.Numeric(14, 3), nullable=False),
        sa.Column('qty_remaining_kg', sa.Numeric(14, 3), nullable=False),
        sa.Column('unit', sa.String(10), nullable=False, server_default='KG'),
        sa.Column('receipt_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(25), nullable=False, server_default='RECEIVED'),
        sa.Column('storage_location', sa.String(100), nullable=True),
        sa.Column('is_contaminated', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 5. production_orders
    op.create_table(
        'production_orders',
        sa.Column('order_id', sa.String(20), primary_key=True),
        sa.Column('product_id', sa.String(20), sa.ForeignKey('products.product_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('planned_qty', sa.Numeric(14, 3), nullable=False),
        sa.Column('actual_qty', sa.Numeric(14, 3), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='PLANNED'),
        sa.Column('location', sa.String(100), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 6. production_consumptions
    op.create_table(
        'production_consumptions',
        sa.Column('consumption_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('order_id', sa.String(20), sa.ForeignKey('production_orders.order_id', ondelete='CASCADE'), nullable=False),
        sa.Column('lot_id', sa.String(60), sa.ForeignKey('material_lots.lot_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('qty_consumed', sa.Numeric(14, 3), nullable=False),
        sa.Column('consumed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 7. finished_lots
    op.create_table(
        'finished_lots',
        sa.Column('lot_id', sa.String(30), primary_key=True),
        sa.Column('order_id', sa.String(20), sa.ForeignKey('production_orders.order_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('product_id', sa.String(20), sa.ForeignKey('products.product_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('quantity_produced', sa.Numeric(14, 3), nullable=False),
        sa.Column('qty_remaining', sa.Numeric(14, 3), nullable=False),
        sa.Column('production_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(25), nullable=False, server_default='IN_WAREHOUSE'),
        sa.Column('storage_location', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 8. lot_genealogy
    op.create_table(
        'lot_genealogy',
        sa.Column('genealogy_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('finished_lot_id', sa.String(30), sa.ForeignKey('finished_lots.lot_id', ondelete='CASCADE'), nullable=False),
        sa.Column('material_lot_id_ref', sa.String(60), nullable=False),
        sa.Column('material_lot_id', sa.String(60), sa.ForeignKey('material_lots.lot_id', ondelete='SET NULL'), nullable=True),
        sa.Column('qty_contributed', sa.Numeric(14, 3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 9. shipments
    op.create_table(
        'shipments',
        sa.Column('shipment_id', sa.String(20), primary_key=True),
        sa.Column('finished_lot_id', sa.String(30), sa.ForeignKey('finished_lots.lot_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('carrier', sa.String(100), nullable=False),
        sa.Column('ship_date', sa.Date(), nullable=False),
        sa.Column('expected_delivery_date', sa.Date(), nullable=False),
        sa.Column('actual_delivery_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='CREATED'),
        sa.Column('qty_shipped', sa.Numeric(14, 3), nullable=False),
        sa.Column('destination_region', sa.String(100), nullable=True),
        sa.Column('tracking_number', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 10. customers
    op.create_table(
        'customers',
        sa.Column('customer_id', sa.String(20), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('country', sa.String(100), nullable=False),
        sa.Column('region', sa.String(100), nullable=False),
        sa.Column('contact_email', sa.String(200), nullable=False),
        sa.Column('contact_phone', sa.String(50), nullable=True),
        sa.Column('tier', sa.String(10), nullable=False, server_default='STANDARD'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 11. deliveries
    op.create_table(
        'deliveries',
        sa.Column('delivery_id', sa.String(20), primary_key=True),
        sa.Column('shipment_id', sa.String(20), sa.ForeignKey('shipments.shipment_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('customer_id', sa.String(20), sa.ForeignKey('customers.customer_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('qty_delivered', sa.Numeric(14, 3), nullable=False),
        sa.Column('delivery_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='DELIVERED'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 12. recall_cases
    op.create_table(
        'recall_cases',
        sa.Column('recall_id', sa.String(20), primary_key=True),
        sa.Column('trigger_type', sa.String(15), nullable=False),
        sa.Column('trigger_lot_id', sa.String(60), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(10), nullable=False, server_default='CLASS_II'),
        sa.Column('initiated_by', sa.String(100), nullable=False),
        sa.Column('initiated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(15), nullable=False, server_default='OPEN'),
        sa.Column('total_qty_affected', sa.Numeric(14, 3), nullable=True),
        sa.Column('total_qty_recovered', sa.Numeric(14, 3), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 13. recall_actions
    op.create_table(
        'recall_actions',
        sa.Column('action_id', sa.String(20), primary_key=True),
        sa.Column('recall_id', sa.String(20), sa.ForeignKey('recall_cases.recall_id', ondelete='CASCADE'), nullable=False),
        sa.Column('action_type', sa.String(15), nullable=False),
        sa.Column('target_entity_type', sa.String(20), nullable=False),
        sa.Column('target_entity_id', sa.String(60), nullable=False),
        sa.Column('qty_affected', sa.Numeric(14, 3), nullable=True),
        sa.Column('qty_actioned', sa.Numeric(14, 3), nullable=True),
        sa.Column('actioned_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('status', sa.String(15), nullable=False, server_default='COMPLETED'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 14. recall_affected_finished_lots
    op.create_table(
        'recall_affected_finished_lots',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('recall_id', sa.String(20), sa.ForeignKey('recall_cases.recall_id', ondelete='CASCADE'), nullable=False),
        sa.Column('finished_lot_id', sa.String(30), sa.ForeignKey('finished_lots.lot_id', ondelete='CASCADE'), nullable=False),
        sa.Column('qty_in_scope', sa.Numeric(14, 3), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 15. recall_affected_deliveries
    op.create_table(
        'recall_affected_deliveries',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('recall_id', sa.String(20), sa.ForeignKey('recall_cases.recall_id', ondelete='CASCADE'), nullable=False),
        sa.Column('delivery_id', sa.String(20), sa.ForeignKey('deliveries.delivery_id', ondelete='CASCADE'), nullable=False),
        sa.Column('qty_in_scope', sa.Numeric(14, 3), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 16. exception_records
    op.create_table(
        'exception_records',
        sa.Column('exception_id', sa.String(20), primary_key=True),
        sa.Column('issue_type', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(60), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('detection_status', sa.String(15), nullable=False, server_default='DETECTED'),
        sa.Column('impact_description', sa.Text(), nullable=False),
        sa.Column('expected_decision', sa.Text(), nullable=False),
        sa.Column('ground_truth_label', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade() -> None:
    op.drop_table('exception_records')
    op.drop_table('recall_affected_deliveries')
    op.drop_table('recall_affected_finished_lots')
    op.drop_table('recall_actions')
    op.drop_table('recall_cases')
    op.drop_table('deliveries')
    op.drop_table('customers')
    op.drop_table('shipments')
    op.drop_table('lot_genealogy')
    op.drop_table('finished_lots')
    op.drop_table('production_consumptions')
    op.drop_table('production_orders')
    op.drop_table('material_lots')
    op.drop_table('bom_items')
    op.drop_table('products')
    op.drop_table('suppliers')

