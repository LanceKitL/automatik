from flask import Blueprint
from validators.middleware import role_required, logged_in_required
from controllers.salesController import (
    #----Sales
    indexSales,
    indexSalesDetails,
    createSales,
    updateSales,
    showMySales,
    showMySalesDetail,
    #----Sales Contracts
    indexSalesContracts,
    createSalesContracts,   
    updateSalesContracts,
    #----Insurance Records
    indexInsuranceRecords,
    createInsuranceRecord,
    updateInsuranceRecord
    
    )

sales_bp = Blueprint("sales", __name__)

#---------------------------------SALES ROUTES---------------------------------
@sales_bp.route("/admin/sales/")
@logged_in_required
@role_required("admin")
def index(): return indexSales() 

@sales_bp.route("/admin/sales/details")
@logged_in_required
@role_required("admin")
def details(): return indexSalesDetails()

@sales_bp.route("/admin/sales/create", methods=["POST"])
@logged_in_required
@role_required("admin")
def create(): return createSales()

@sales_bp.route("/admin/sales/update/<int:sale_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update(sale_id): return updateSales(sale_id)

@sales_bp.route("/my-sales")
@logged_in_required
@role_required("customer")
def my_sales(): return showMySales()

@sales_bp.route("/my-sales/details")
@logged_in_required
@role_required("customer")
def my_sales_details(): return showMySalesDetail()


#-----------------------------SALES CONTRACTS ROUTES-----------------------------

@sales_bp.route("/admin/sales-contracts")
@logged_in_required
@role_required("admin", and_="agent")
def sales_contracts(): return indexSalesContracts()

@sales_bp.route("/admin/sales-contracts/create", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_sales_contract(): return createSalesContracts()

@sales_bp.route("/admin/sales-contracts/update/<int:contract_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_sales_contract(contract_id): return updateSalesContracts(contract_id)


#-----------------------------INSURANCE RECORDS ROUTES-----------------------------

@sales_bp.route("/admin/insurance-records")
@logged_in_required
@role_required("admin")
def insurance_records(): return indexInsuranceRecords()

@sales_bp.route("/admin/insurance-records/create", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_insurance_record(): return createInsuranceRecord()


@sales_bp.route("/admin/insurance-records/update/<int:insurance_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_insurance_record(insurance_id): return updateInsuranceRecord(insurance_id)




