from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models, Command
from odoo.tools.float_utils import float_round


class AccountMoveAResultOpt(models.Model):
    _name = "account.move.a.result.opt"
    _description = "Invoice Analysis Result Option"
    
    move_id = fields.Many2one("account.move", ondelete="cascade")
    name = fields.Char(required=True)
    value = fields.Float(required=True)


class AccountMove(models.Model):
    _inherit = "account.move"
    
    round_cif = fields.Boolean('Enable Rounding (CIF)')
    rounding_cif = fields.Float('Rounding (CIF)', default=0)
    rounding_cif_method = fields.Selection([
        ('UP', 'Up'),
        ('DOWN', 'Down'),
        ('HALF-UP', 'Nearest')
    ], default='HALF-UP', string='Rounding Method (CIF)')
    
    round_hpm = fields.Boolean('Enable Rounding (HPM)')
    rounding_hpm = fields.Float('Rounding (HPM)', default=0)
    rounding_hpm_method = fields.Selection([
        ('UP', 'Up'),
        ('DOWN', 'Down'),
        ('HALF-UP', 'Nearest')
    ], default='HALF-UP', string='Rounding Method (HPM)')
    
    round_fob = fields.Boolean('Enable Rounding (FOB)')
    rounding_fob = fields.Float('Rounding (FOB)', default=0)
    rounding_fob_method = fields.Selection([
        ('UP', 'Up'),
        ('DOWN', 'Down'),
        ('HALF-UP', 'Nearest')
    ], default='HALF-UP', string='Rounding Method (FOB)')
    
    round_freight = fields.Boolean('Enable Rounding (Freight)')
    rounding_freight = fields.Float('Rounding (Freight)', default=0)
    rounding_freight_method = fields.Selection([
        ('UP', 'Up'),
        ('DOWN', 'Down'),
        ('HALF-UP', 'Nearest')
    ], default='HALF-UP', string='Rounding Method (Freight)')
    
    round_weight = fields.Boolean('Enable Rounding (Weight)')
    rounding_weight = fields.Float('Rounding (Weight)', default=0)
    rounding_weight_method = fields.Selection([
        ('UP', 'Up'),
        ('DOWN', 'Down'),
        ('HALF-UP', 'Nearest')
    ], default='HALF-UP', string='Rounding Method (Weight)')
    
    round_price_unit = fields.Boolean('Enable Rounding (Price Unit)')
    rounding_price_unit = fields.Float('Rounding (Price Unit)', default=0)
    rounding_price_unit_method = fields.Selection([
        ('UP', 'Up'),
        ('DOWN', 'Down'),
        ('HALF-UP', 'Nearest')
    ], default='HALF-UP', string='Rounding Method (Price Unit)')
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        bank = self.env["res.bank"].sudo()
        company = self.env.company.sudo()
        if not company.bank_account_ids:
            bank_id = bank.search([
                ("name", "=ilike", "mandiri"),
            ], limit=1)
            if not bank_id:
                bank_id = bank.create({"name": "Mandiri"})
            company.bank_account_ids = [Command.create({
                "acc_number": "122-00-0771383-0",
                "bank_id": bank_id.id,
                "branch": "KCP Jakarta Ratu Plaza",
                "acc_holder_name": "PT Stargate Pasific Resources",
                "partner_id": company.partner_id.id,
            })]
        res["partner_bank_id"] = company.bank_account_ids.ids[0]
        return res
    
    def float_round(self, value, target=None):
        self.ensure_one()
        if target and hasattr(self, f"round_{target}"):
            if getattr(self, f"round_{target}", False):
                rounding = 10 ** (-getattr(self, f"rounding_{target}", 0))
                rounding_method = getattr(self, f"rounding_{target}_method", "HALF-UP")
                if  rounding and rounding_method:
                    return float_round(value, precision_rounding=rounding, rounding_method=rounding_method)
        elif self.round_subtotal:
            rounding = 10 ** (-self.rounding)
            rounding_method = self.rounding_method
            if  rounding and rounding_method:
                return float_round(value, precision_rounding=rounding, rounding_method=rounding_method)
        return value

    invoice_type_id = fields.Many2one(
        comodel_name="account.move.type", string="Invoice Type"
    )
    invoice_type_code = fields.Char(
        related="invoice_type_id.code", string="Invoice Type Code"
    )
    skip_compute_name_regex = fields.Boolean(default=False)

    # Calculate Tab Fields
    # ==========================================================

    # General Information
    contract_number = fields.Char(string="No. Kontrak")
    contract_sequence = fields.Char(string="No. Urut Kontrak")
    shipment_number = fields.Char(string="No. Kapal")
    barging_number = fields.Char(string="No. Barging")
    bl_number = fields.Char(string="BL Number")
    bl_date = fields.Date(string="BL Date")
    draft_survey_weight = fields.Float(
        string="Draft Survey Weight", default=0.0, digits=(None, 3)
    )
    assigner_id = fields.Many2one(comodel_name="hr.employee", string="Assigner")
    assigner_job_title = fields.Char(
        string="Job Title", related="assigner_id.job_title", readonly=True
    )
    currency_contract_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )
    rate_type = fields.Selection(
        selection=[("bi_rate", "BI Rate"), ("kmk_rate", "KMK Rate")],
        string="Rate Type",
        default="bi_rate",
    )
    bi_rate = fields.Float(string="Rate", digits=(16, 6), default=0.0)
    bi_rate_date = fields.Date(string="Rate Date")
    vat = fields.Float(string="VAT", digits=(3, 2), default=0.0)
    price_unit = fields.Float(
        string="Unit Price",
        digits='Product Price',
        compute="_compute_price_unit",
        store=True,
        readonly=False,
    )

    # Analysis Result
    minerale_ni = fields.Float(string="Ni", digits=(3, 2), default=0.0)
    minerale_co = fields.Float(string="Co", digits=(3, 2), default=0.0)
    minerale_fe = fields.Float(string="Fe", digits=(3, 2), default=0.0)
    minerale_sio = fields.Float(string="SiO2/MgO", digits=(3, 2), default=0.0)
    minerale_al2o3 = fields.Float(string="Al2O3", digits=(3, 2), default=0.0)
    minerale_h2o = fields.Float(string="H2O", digits=(3, 2), default=0.0)

    # Provisional Invoice
    orders_amount = fields.Float(string="Orders Amount", digits=(16, 4), default=0.0)
    percentage = fields.Float(string="Provisional Percentage", default=0.0)
    provisional_amount = fields.Float(
        string="Provisional Value", compute="_compute_percentage", store=True
    )
    percentage_balance = fields.Float(
        string="Provisional Balance", compute="_compute_percentage", store=True
    )

    # Final Invoice
    settlement_weight = fields.Float(
        string="Settlement Weight",
        digits=(None, 3),
        compute="_compute_settlement_weight",
        store=True,
    )
    ore_type = fields.Selection(
        selection=[("saprolite", "Saprolite"), ("limonite", "Limonite")],
        string="Ore Type",
    )
    use_quantity_type = fields.Selection(
        selection=[
            ("survey", "Draft Survey Weight"),
            ("settlement", "Settlement Weight"),
        ],
        default="survey",
    )

    # Final Saprolite
    sp_correction_factor = fields.Float(
        string="Correction Factor",
        compute="_compute_sp_correction_factor",
        store=True,
        digits=(3, 2),
    )
    sp_hma_nickel = fields.Float(string="HMA Nickel")
    sp_mc = fields.Float(
        string="(1-%MC)", compute="_compute_sp_mc", store=True, digits=(3, 2)
    )
    sp_hpm_price = fields.Float(
        string="HPM Price", compute="_compute_sp_hpm_price", store=True
    )
    sp_ni_adjustment = fields.Float(string="SiO2/MgO Adjustment", default=0.0)
    sp_custom_label = fields.Char()
    sp_custom_value = fields.Float(default=0.0)
    sp_fob_amount = fields.Float(
        string="Final FOB Price", compute="_compute_sp_fob_price", store=True
    )
    sp_freight_amount = fields.Float(string="Freight", default=0.0)
    sp_cif_amount = fields.Float(
        string="Total CIF Price", compute="_compute_sp_cif_price", store=True
    )

    # Final Limonite
    # Label mengikuti Excel finance (basis Ni 1,20%). Nama field lama
    # dipertahankan supaya data invoice Limonite lama tidak perlu dimigrasi:
    # lm_ni_penalty_13* = penalty di bawah 1,20%, lm_ni_penalty_10* = di bawah 1,00%.
    lm_ni_fob = fields.Float(
        string="Ni 1.20% FOB Price", compute="_compute_lm_ni_fob", store=True
    )
    lm_ni_fob_qty = fields.Float(string="Ni 1.20% FOB Quantity", default=0.0)
    lm_ni_fob_price = fields.Float(string="Ni 1.20% FOB Unit Price", default=0.0)
    lm_ni_bonus = fields.Float(
        string="Ni > 1.30% Bonus", compute="_compute_lm_ni_bonus", store=True
    )
    lm_ni_bonus_qty = fields.Float(string="Ni > 1.30% Bonus Quantity")
    lm_ni_bonus_price = fields.Float(string="Ni > 1.30% Bonus Price", default=0.0)
    lm_ni_bonus_12 = fields.Float(
        string="Ni > 1.20% Bonus", compute="_compute_lm_ni_bonus_12", store=True
    )
    lm_ni_bonus_12_qty = fields.Float(string="Ni > 1.20% Bonus Quantity")
    lm_ni_bonus_12_price = fields.Float(string="Ni > 1.20% Bonus Price", default=0.0)
    lm_ni_penalty_13 = fields.Float(
        string="Ni < 1.20% Penalty", compute="_compute_lm_ni_penalty_13", store=True
    )
    lm_ni_penalty_13_qty = fields.Float(string="Ni < 1.20% Penalty Quantity")
    lm_ni_penalty_13_price = fields.Float(
        string="Ni < 1.20% Penalty Price", default=0.0
    )
    lm_ni_penalty_10 = fields.Float(
        string="Ni < 1.00% Penalty", compute="_compute_lm_ni_penalty_10", store=True
    )
    lm_ni_penalty_10_qty = fields.Float(string="Ni < 1.00% Penalty Quantity")
    lm_ni_penalty_10_price = fields.Float(
        string="Ni < 1.00% Penalty Price", default=0.0
    )
    lm_co_bonus = fields.Float(
        string="Co Bonus", compute="_compute_lm_co_bonus", store=True
    )
    lm_co_bonus_qty = fields.Float(string="Co Bonus Quantity", default=0.0)
    lm_co_bonus_price = fields.Float(string="Co Bonus Price", default=0.0)
    lm_h20_penalty = fields.Float(
        string="H2O Penalty", compute="_compute_lm_h20_penalty", store=True
    )
    lm_h20_penalty_qty = fields.Float(string="H2O Penalty Quantity", default=0.0)
    lm_h20_penalty_price = fields.Float(string="H2O Penalty Price", default=0.0)
    lm_label_custom = fields.Char()
    lm_custom = fields.Float(compute="_compute_lm_custom", store=True)
    lm_custom_qty = fields.Float(default=0.0)
    lm_custom_price = fields.Float(default=0.0)
    lm_fob_amount = fields.Float(
        string="Final FOB Price", compute="_compute_lm_fob_amount", store=True
    )
    lm_freight_amount = fields.Float(
        string="Freight", compute="_compute_lm_freight_amount", store=True
    )
    lm_freight_amount_qty = fields.Float(string="Freight Quantity", default=0.0)
    lm_freight_amount_price = fields.Float(string="Freight Price", default=0.0)
    lm_cif_amount = fields.Float(
        string="Total CIF Price", compute="_compute_lm_cif_amount", store=True
    )

    price_unit_bi = fields.Float(compute="_compute_price_unit_bi", store=True, digits='Product Price')
    # ==========================================================

    # Nomer invoice provisional (INVP)-(YYYYMMDD *invoice date)-(kode customer [3 digit], nomer kontrak [3 digit])-(no urutan kapall [2 digit], nomor Barging  [3 digit])+ (Sequence (config))
    # Nomer invoice Final (INVF)-(YYYYMMDD *invoice date)-(kode customer [3 digit], nomer kontrak [3 digit])-(no urutan kapall [2 digit], nomor Barging  [3 digit])

    a_result_opt_ids = fields.One2many("account.move.a.result.opt", "move_id", string="Optional")
    
    def get_custom_sequence(self):
        self.ensure_one()
        move = self
        move_has_name = move.name and move.name.lower() not in ["draft", "/"]
        sequence_number_arr = []

        # Update
        if move_has_name:
            sequence_number = move.name
            sequence_number_arr = sequence_number.split("-")

            if move.invoice_date:
                sequence_number_arr[1] = move.invoice_date.strftime("%Y%m%d")

            if move.partner_id.external_id or move.contract_sequence:
                contract_sequence = "".join(
                    [
                        move.partner_id.external_id
                        if move.partner_id.external_id
                        else "XXX",
                        move.contract_sequence
                        if move.contract_sequence
                        else "XXX",
                    ]
                )
                sequence_number_arr[2] = contract_sequence

            if move.shipment_number or move.barging_number:
                shipment_barging = "".join(
                    [
                        move.shipment_number if move.shipment_number else "XX",
                        move.barging_number if move.barging_number else "XXX",
                    ]
                )
                sequence_number_arr[3] = shipment_barging

        # Create
        else:
            sequence_number = move.invoice_type_id.sequence_id.next_by_id()
            sequence_number_arr = sequence_number.split("-")

            if move.invoice_date:
                sequence_number_arr.insert(
                    1, move.invoice_date.strftime("%Y%m%d")
                )

            if move.partner_id.external_id or move.contract_sequence:
                contract_sequence = "".join(
                    [
                        move.partner_id.external_id
                        if move.partner_id.external_id
                        else "XXX",
                        move.contract_sequence
                        if move.contract_sequence
                        else "XXX",
                    ]
                )
                sequence_number_arr.insert(2, contract_sequence)

            if move.shipment_number or move.barging_number:
                shipment_barging = "".join(
                    [
                        move.shipment_number if move.shipment_number else "XX",
                        move.barging_number if move.barging_number else "XXX",
                    ]
                )
                sequence_number_arr.insert(3, shipment_barging)

        move.name = "-".join(sequence_number_arr)

    # Origin compute name
    def _compute_name(self):
        for move in self:
            if move.skip_compute_name_regex and move.state == "posted":
                move.get_custom_sequence()
            else:
                return super()._compute_name()

    # Account Move Number Sequence compute name
    # Without depend to account_move_name_sequence
    @api.depends("state", "journal_id", "date")
    def _compute_name_by_sequence(self):
        for move in self:
            if move.skip_compute_name_regex and move.state == "posted":
                move.get_custom_sequence()
            else:
                return super()._compute_name_by_sequence()

    @api.depends(
        "round_price_unit",
        "rounding_price_unit",
        "rounding_price_unit_method",
        "invoice_type_code",
        "invoice_type_id",
        "ore_type",
        "sp_cif_amount",
        "lm_cif_amount",
        "bi_rate",
    )
    def _compute_price_unit(self):
        for move in self:
            price_unit = move.price_unit if move.price_unit else 0.0
            if move.invoice_type_code == "final":
                if move.ore_type == "saprolite":
                    price_unit = move.sp_cif_amount * move.bi_rate
                elif move.ore_type == "limonite":
                    price_unit = move.lm_cif_amount * move.bi_rate
                move.price_unit = move.float_round(price_unit, target="price_unit")

    @api.depends(
        "round_price_unit",
        "rounding_price_unit",
        "rounding_price_unit_method",
        "price_unit",
        "bi_rate",
        "invoice_type_code",
        "invoice_type_id",
    )
    def _compute_price_unit_bi(self):
        for move in self:
            move.price_unit_bi = move.price_unit if move.price_unit != 0.0 else 0.0
            if move.invoice_type_code != "final":
                if move.bi_rate != 0.0:
                    move.price_unit_bi = move.price_unit * move.bi_rate
                else:
                    move.price_unit_bi = move.price_unit
                # move.price_unit_bi = move.float_round(move.price_unit_bi, target="price_unit")

    @api.depends("percentage", "draft_survey_weight", "price_unit", "bi_rate")
    def _compute_percentage(self):
        for move in self:
            percentage_balance = provisional_amount = 0.0
            if move.percentage:
                percentage_balance = 100 - move.percentage
                provisional_amount = (
                    move.draft_survey_weight
                    * (move.price_unit * move.bi_rate)
                    * (move.percentage / 100)
                )
            move.percentage_balance = percentage_balance
            move.provisional_amount = move.float_round(provisional_amount, target="price_unit")

    def get_rounded_value(self, value, precision_digits=2):
        # Use Decimal for precise rounding (ROUND_HALF_UP, not banker's rounding)
        quantize_str = "1." + "0" * precision_digits
        result = Decimal(str(value)).quantize(
            Decimal(quantize_str), rounding=ROUND_HALF_UP
        )
        return float(result)

    def set_quantity_final(self):
        self.use_quantity_type = self._context.get("default_use_quantity_type", False)
        
    @api.constrains("round_weight", "rounding_weight", "rounding_weight_method", "draft_survey_weight")
    def _check_draft_survey_weight(self):
        for rec in self:
            draft_survey_weight = rec.float_round(rec.draft_survey_weight, target="weight")
            if rec.draft_survey_weight != draft_survey_weight:
                rec.draft_survey_weight = draft_survey_weight

    @api.depends("round_weight", "rounding_weight", "rounding_weight_method", "draft_survey_weight", "minerale_h2o")
    def _compute_settlement_weight(self):
        for move in self:
            settlement_weight = move.draft_survey_weight * (
                1 - ((move.minerale_h2o - 35) / 100)
            )
            move.settlement_weight = move.float_round(settlement_weight, target="weight")

    # Saprolite
    # ==========================================================

    @api.depends("minerale_ni")
    def _compute_sp_correction_factor(self):
        for move in self:
            correction_factor = 0.0
            if move.minerale_ni:
                if move.minerale_ni == 1.9:
                    correction_factor = 20
                elif move.minerale_ni < 1.9:
                    correction_factor = 20 - ((1.9 - move.minerale_ni) * 10)
                else:
                    correction_factor = 20 + ((move.minerale_ni - 1.9) * 10)
            move.sp_correction_factor = correction_factor

    @api.depends("minerale_h2o")
    def _compute_sp_mc(self):
        for move in self:
            mc = 0.0
            if move.minerale_h2o:
                mc = 100 - move.minerale_h2o
            move.sp_mc = mc

    @api.depends("round_hpm", "rounding_hpm", "rounding_hpm_method", "minerale_ni", "sp_correction_factor", "sp_hma_nickel", "sp_mc")
    def _compute_sp_hpm_price(self):
        for move in self:
            sp_hpm_price = 0.0
            if (
                move.minerale_ni
                and move.sp_correction_factor
                and move.sp_hma_nickel
                and move.sp_mc
            ):
                sp_hpm_price = (
                    (move.minerale_ni / 100)
                    * (move.sp_correction_factor / 100)
                    * (move.sp_hma_nickel)
                    * (move.sp_mc / 100)
                )
            move.sp_hpm_price = move.float_round(sp_hpm_price, target="hpm")

    @api.depends("round_fob", "rounding_fob", "rounding_fob_method", "sp_hpm_price", "sp_ni_adjustment", "sp_custom_label", "sp_custom_value")
    def _compute_sp_fob_price(self):
        for move in self:
            sp_fob_amount = 0.0
            if move.sp_hpm_price:
                sp_fob_amount = move.sp_hpm_price + move.sp_ni_adjustment
            if move.sp_custom_label:
                sp_fob_amount += move.sp_custom_value
            move.sp_fob_amount = move.float_round(sp_fob_amount, target="fob")

    @api.depends("round_cif", "rounding_cif", "rounding_cif_method", "sp_fob_amount", "sp_freight_amount")
    def _compute_sp_cif_price(self):
        for move in self:
            sp_cif_amount = 0.0
            if move.sp_fob_amount and move.sp_freight_amount:
                sp_cif_amount = move.sp_fob_amount + move.sp_freight_amount
            move.sp_cif_amount = move.float_round(sp_cif_amount, target="cif")

    # Limonite
    # ==========================================================

    @api.depends("lm_ni_fob_qty", "lm_ni_fob_price")
    def _compute_lm_ni_fob(self):
        for move in self:
            move.lm_ni_fob = move.lm_ni_fob_qty * move.lm_ni_fob_price

    @api.depends("minerale_ni", "lm_ni_bonus_price", "lm_ni_bonus_qty")
    def _compute_lm_ni_bonus(self):
        for move in self:
            move.lm_ni_bonus = (move.lm_ni_bonus_qty * 100) * move.lm_ni_bonus_price

    @api.depends("lm_ni_bonus_12_qty", "lm_ni_bonus_12_price")
    def _compute_lm_ni_bonus_12(self):
        for move in self:
            move.lm_ni_bonus_12 = (
                move.lm_ni_bonus_12_qty * 100
            ) * move.lm_ni_bonus_12_price

    @api.depends("lm_ni_penalty_13_qty", "lm_ni_penalty_13_price")
    def _compute_lm_ni_penalty_13(self):
        for move in self:
            move.lm_ni_penalty_13 = (
                move.lm_ni_penalty_13_qty * 100
            ) * move.lm_ni_penalty_13_price

    @api.depends("lm_ni_penalty_10_qty", "lm_ni_penalty_10_price")
    def _compute_lm_ni_penalty_10(self):
        for move in self:
            move.lm_ni_penalty_10 = (
                move.lm_ni_penalty_10_qty * 100
            ) * move.lm_ni_penalty_10_price

    @api.depends("lm_co_bonus_qty", "lm_co_bonus_price")
    def _compute_lm_co_bonus(self):
        for move in self:
            move.lm_co_bonus = move.lm_co_bonus_qty * move.lm_co_bonus_price * 100.0

    @api.depends("lm_h20_penalty_qty", "lm_h20_penalty_price")
    def _compute_lm_h20_penalty(self):
        for move in self:
            move.lm_h20_penalty = move.lm_h20_penalty_qty * move.lm_h20_penalty_price

    @api.depends("lm_custom_qty", "lm_custom_price")
    def _compute_lm_custom(self):
        for move in self:
            move.lm_custom = (move.lm_custom_qty * 100) * move.lm_custom_price

    @api.depends(
        "round_fob",
        "rounding_fob",
        "rounding_fob_method",
        "lm_ni_fob",
        "lm_ni_bonus",
        "lm_ni_bonus_12",
        "lm_ni_penalty_13",
        "lm_ni_penalty_10",
        "lm_co_bonus",
        "lm_h20_penalty",
        "lm_custom",
        "lm_custom_qty",
        "lm_custom_price",
    )
    def _compute_lm_fob_amount(self):
        self._compute_lm_custom()
        for move in self:
            move.lm_fob_amount = (
                move.lm_ni_fob
                +move.lm_ni_bonus
                +move.lm_ni_bonus_12
                +move.lm_ni_penalty_13
                +move.lm_ni_penalty_10
                +move.lm_co_bonus
                +move.lm_h20_penalty
                +move.lm_custom
            )
            move.lm_fob_amount = move.float_round(move.lm_fob_amount, target="fob")

    @api.depends("round_freight", "rounding_freight", "rounding_freight_method", "lm_freight_amount_qty", "lm_freight_amount_price")
    def _compute_lm_freight_amount(self):
        for move in self:
            move.lm_freight_amount = (
                move.lm_freight_amount_qty * move.lm_freight_amount_price
            )
            move.lm_freight_amount = move.float_round(move.lm_freight_amount, target="freight")

    @api.depends("round_cif", "rounding_cif", "rounding_cif_method", "lm_fob_amount", "lm_freight_amount")
    def _compute_lm_cif_amount(self):
        self._compute_lm_fob_amount()
        self._compute_lm_freight_amount()
        for move in self:
            move.lm_cif_amount = move.lm_fob_amount + move.lm_freight_amount
            move.lm_cif_amount = move.float_round(move.lm_cif_amount, target="cif")
