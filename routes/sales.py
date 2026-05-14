from flask import Blueprint, request, session, jsonify
from validators.middleware import role_required 
from conn import run_query
from controllers.salesController import(
    createSale,
    searchSales,
    updateSale,
    deleteSale
)   

sales_bp = Blueprint('sales', __name__)

#List all sales
@sales_bp.route('/')
def sales ():
    res = run_query("SELECT * FROM sales", fetch= "all")
    return jsonify ({"data": res}), 200

#Create Sale
@sales_bp.route('/', methods = ['POST'])
@role_required('admin')
def add_sale(): return createSale()

#Get Sale
@sales_bp.route('/<int:id>')
def get_sale(id):
     res = run_query("SELECT * FROM sales WHERE sale_id = %s", (id,),fetch="one")

     if not res:
          return jsonify ({"message": "Sale not found"}), 400
     
     return jsonify ({"data": res}), 200

#Update Sale
@sales_bp.route('/<int:id>', methods = ['PUT'])
@role_required('admin')
def update_sale(id): return updateSale(id)

#Delete Sale
@sales_bp.route('/<int:id>', methods = ['DELETE'])
@role_required('admin')
def delete_sale(id): return deleteSale(id)