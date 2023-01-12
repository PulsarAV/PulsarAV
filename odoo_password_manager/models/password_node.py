# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class password_node(models.AbstractModel):
    """
    This is the Abstract Model to manage jstree nodes
    It is used for password tags
    """
    _name = "password.node"
    _description = "Password Node"

    @api.constrains("parent_id")
    def _check_node_recursion(self):
        """
        Constraint for recursion
        """
        if not self._check_recursion():
            raise ValidationError(_("Recursions are not allowed!"))
        return True

    def _inverse_bundle_id(self):
        """
        Inverse method for bundle_id
        If node bundle is changed, we firstly check it suits the parent and then update all child nodes to the same 
        bundle
        """
        for node in self:
            if node.parent_id and node.parent_id.bundle_id != node.bundle_id:
                node.bundle_id = node.parent_id.bundle_id
            else:
                node.child_ids.write({"bundle_id": node.bundle_id.id}) # recursion

    def _inverse_active(self):
        """
        Inverse method for active. There 2 goals:
         1. If a parent is not active, we activate it. It recursively activate all its further parents
         2. Deacticate all children. It will invoke deactivation recursively of all children after
        """
        for node in self:
            if node.active:
                # 1
                if node.parent_id and not node.parent_id.active:
                    node.parent_id.active = True
            else:
                # 2
                node.child_ids.write({"active": False})

    bundle_id = fields.Many2one(
        "password.bundle", 
        string="Bundle", 
        ondelete="cascade",
        inverse=_inverse_bundle_id,
    )
    active = fields.Boolean(string="Active", default=True, inverse=_inverse_active)
    sequence = fields.Integer(string="Sequence", default=0)
    
    def name_get(self):
        """
        Overloading the method, to reflect parent's name recursively
        """
        result = []
        for node in self:
            name = u"{}{}".format(node.parent_id and node.parent_id.name_get()[0][1] + "/" or "", node.name)
            result.append((node.id, name))
        return result

    @api.model
    def _return_nodes(self, bundle_ids):
        """
        The method to return nodes in jstree format

        Args:
         * bundle_ids - list of password.bundle ids

        Methods:
         * _return_nodes_recursive

        Returns:
         * list of folders dict with keys:
           ** id
           ** text - folder_name
           ** children - array with the same keys
        """
        node_domain = [("parent_id", "=", False)]
        if bundle_ids:
            node_domain += ["|", ("bundle_id", "in", bundle_ids), ("bundle_id", "=", False)]
        nodes = self.search(node_domain)
        res = []
        for node in nodes:
            res.append(node._return_nodes_recursive())
        return res

    def return_nodes_with_restriction(self):
        """
        The method to return nodes in recursion for that actual nodes. Not for all

        Methods:
         * _return_nodes_recursive

        Returns:
         * list of folders dict with keys:
           ** id
           ** text - folder_name
           ** children - array with the same keys
        """
        nodes = self.search([
            ("id", "in", self.ids),
            "|",
                ("parent_id", "=", False),
                ("parent_id", "not in", self.ids),
        ])
        res = []
        for node in nodes:
            res.append(node._return_nodes_recursive(restrict_nodes=self))
        return res

    def _return_nodes_recursive(self, restrict_nodes=False):
        """
        The method to go by all nodes recursively to prepare their list in js_tree format

        Args:
         * nodes - optional param to restrict child with current nodes

        Extra info:
         * sorted needed to fix unclear bug of zero-sequence element placed to the end
         * Expected singleton
        """
        res = {"text": self.name, "id": self.id}
        child_res = []
        child_ids = self.search([("id", "in", self.child_ids.ids)], order="sequence")
        for child in child_ids:
            if restrict_nodes and child not in restrict_nodes:
                continue
            child_res.append(child._return_nodes_recursive())
        res.update({"children": child_res})
        return res

    @api.model
    def create_node(self, data, bundle_id=False):
        """
        The method to update node name

        Methods:
         * _order_node_after_dnd

        Returns:
         * int - id of newly created record
        """
        name = data.get("text")
        parent_id = data.get("parent")
        node_bundle_id = None
        if parent_id == "#":
            parent_id = False
        else:
            parent_id = int(parent_id)
            parent_obj = self.browse(parent_id)
            if parent_obj.exists():
                # parent bundle is prioritized
                node_bundle_id = parent_obj.bundle_id.id
            else:
                parent_id = False
        
        new_node_vals = {
            "name": name, 
            "parent_id": parent_id, 
            "bundle_id": node_bundle_id is not None and node_bundle_id or bundle_id
        }
        new_node = self.create([new_node_vals])
        new_node._order_node_after_dnd(parent_id=parent_id, position=False)
        return new_node.id

    def update_node(self, data, position):
        """
        The method to update node name

        Args:
         * data - dict of node params
         * position - false (in case it is rename) or int (in case it is move)

        Methods:
         * _order_node_after_dnd

        Returns:
         * int - id of udpated record

        Extra info:
         * Expected singleton
        """
        new_name = data.get("text")
        new_parent_id = data.get("parent")
        new_parent_id = new_parent_id != "#" and int(new_parent_id) or False
        node_bundle_id = None
        if new_parent_id:
            parent_obj = self.browse(new_parent_id)
            if parent_obj.exists():
                # get parent bundle if parent is changed
                node_bundle_id = parent_obj.bundle_id
            else:
                new_parent_id = False
        if self.name != new_name:
            self.name = new_name
        if self.parent_id.id != new_parent_id:
            self.parent_id = new_parent_id
        if node_bundle_id is not None and self.bundle_id != node_bundle_id:
            self.bundle_id = node_bundle_id
        if position is not False:
            self._order_node_after_dnd(parent_id=new_parent_id, position=position)
        return self.id

    def delete_node(self):
        """
        The method to deactivate a node
        It triggers recursive deactivation of children

        Returns:
         * int - id of udpated record

        Extra info:
         * Expected singleton
        """
        self.active = False
        return True

    def _order_node_after_dnd(self, parent_id, position):
        """
        The method to normalize sequence when position of Node has been changed based on a new element position and
        its neighbours.
         1. In case of create we put element always to the end
         2. We try to update all previous elements sequences in case it become the same of a current one (sequence
            migth be negative)

        Args:
         * parent_id - int - id of node
         * position - int or false (needed to the case of create)

        Extra info:
         * Epected singleton
        """
        the_same_children_domain = [("id", "!=", self.id)]
        if parent_id:
            the_same_children_domain.append(("parent_id.id", "=", parent_id))
        else:
            the_same_children_domain.append(("parent_id", "=", False))
        this_parent_nodes = self.search(the_same_children_domain)
        if position is False:
            position = len(this_parent_nodes)
        if this_parent_nodes:
            neigbour_after = len(this_parent_nodes) > position and this_parent_nodes[position] or False
            neigbour_before = position > 0 and this_parent_nodes[position-1] or False
            sequence = False
            if neigbour_after:
                sequence = neigbour_after.sequence - 1
                # 1
                while neigbour_before and neigbour_before.sequence == sequence:
                    neigbour_before.sequence = neigbour_before.sequence - 1
                    position -= 1
                    neigbour_before = position > 0 and this_parent_nodes[position-1] or False
            elif neigbour_before:
                sequence = neigbour_before.sequence + 1
            if sequence is not False:
                self.sequence = sequence
