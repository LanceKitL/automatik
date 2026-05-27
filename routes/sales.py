from flask import Blueprint
from controllers.salesController import (
    indexSales
    )

sales_bp = Blueprint("sales", __name__)


@sales_bp.route("/")
def index(): return indexSales() 