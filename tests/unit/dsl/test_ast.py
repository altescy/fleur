"""Unit tests for AST node creation and structure."""

from fleur.dsl import ast


class TestLiteralNodes:
    """Tests for literal AST nodes."""

    def test_number_node_creation(self):
        """Test creating a number node."""
        node = ast.GraineNumberNode(value=42.0)
        assert node.value == 42.0

    def test_string_node_creation(self):
        """Test creating a string node."""
        node = ast.GraineStringNode(value="hello")
        assert node.value == "hello"

    def test_boolean_node_creation(self):
        """Test creating a boolean node."""
        node_true = ast.GraineBooleanNode(value=True)
        node_false = ast.GraineBooleanNode(value=False)
        assert node_true.value is True
        assert node_false.value is False

    def test_array_node_empty(self):
        """Test creating an empty array node."""
        node = ast.GraineArrayNode()
        assert node.elements == []

    def test_array_node_with_elements(self):
        """Test creating an array node with elements."""
        elem1 = ast.GraineNumberNode(value=1.0)
        elem2 = ast.GraineNumberNode(value=2.0)
        node = ast.GraineArrayNode(elements=[elem1, elem2])
        assert len(node.elements) == 2
        # Use isinstance to narrow type for type checker
        elem0 = node.elements[0]
        assert isinstance(elem0, ast.GraineNumberNode)
        assert elem0.value == 1.0
        elem1_check = node.elements[1]
        assert isinstance(elem1_check, ast.GraineNumberNode)
        assert elem1_check.value == 2.0

    def test_record_node_empty(self):
        """Test creating an empty record node."""
        node = ast.GraineRecordNode()
        assert node.fields == {}

    def test_record_node_with_fields(self):
        """Test creating a record node with fields."""
        value = ast.GraineNumberNode(value=42.0)
        node = ast.GraineRecordNode(fields={"x": value})
        assert "x" in node.fields
        # Use isinstance to narrow type
        field_x = node.fields["x"]
        assert isinstance(field_x, ast.GraineNumberNode)
        assert field_x.value == 42.0


class TestExpressionNodes:
    """Tests for expression AST nodes."""

    def test_identifier_node(self):
        """Test creating an identifier node."""
        node = ast.GraineIdentifierNode(name="myVar")
        assert node.name == "myVar"

    def test_binary_op_node(self):
        """Test creating a binary operation node."""
        left = ast.GraineNumberNode(value=1.0)
        right = ast.GraineNumberNode(value=2.0)
        node = ast.GraineBinaryOpNode(op="+", left=left, right=right)
        assert node.op == "+"
        # Type narrowing for operands
        assert isinstance(node.left, ast.GraineNumberNode)
        assert node.left.value == 1.0
        assert isinstance(node.right, ast.GraineNumberNode)
        assert node.right.value == 2.0

    def test_call_node_no_args(self):
        """Test creating a call node without arguments."""
        func = ast.GraineIdentifierNode(name="myFunc")
        node = ast.GraineCallNode(function=func)
        # Type narrowing for function
        assert isinstance(node.function, ast.GraineIdentifierNode)
        assert node.function.name == "myFunc"
        assert node.arguments == []

    def test_call_node_with_args(self):
        """Test creating a call node with arguments."""
        func = ast.GraineIdentifierNode(name="add")
        arg1 = ast.GraineNumberNode(value=1.0)
        arg2 = ast.GraineNumberNode(value=2.0)
        node = ast.GraineCallNode(function=func, arguments=[arg1, arg2])
        assert len(node.arguments) == 2

    def test_property_access_node(self):
        """Test creating a property access node."""
        receiver = ast.GraineIdentifierNode(name="obj")
        node = ast.GrainePropertyAccessNode(property_name="prop", receiver=receiver)
        assert node.property_name == "prop"
        # Type narrowing
        assert isinstance(node.receiver, ast.GraineIdentifierNode)
        assert node.receiver.name == "obj"

    def test_index_access_node(self):
        """Test creating an index access node."""
        receiver = ast.GraineIdentifierNode(name="arr")
        index = ast.GraineNumberNode(value=0.0)
        node = ast.GraineIndexAccessNode(index=index, receiver=receiver)
        # Type narrowing
        assert isinstance(node.index, ast.GraineNumberNode)
        assert node.index.value == 0.0
        assert isinstance(node.receiver, ast.GraineIdentifierNode)
        assert node.receiver.name == "arr"

    def test_conditional_node_with_else(self):
        """Test creating a conditional node with else branch."""
        condition = ast.GraineBooleanNode(value=True)
        then_branch = ast.GraineNumberNode(value=1.0)
        else_branch = ast.GraineNumberNode(value=2.0)
        node = ast.GraineConditionalNode(condition=condition, then_branch=then_branch, else_branch=else_branch)
        # Type narrowing for all branches
        assert isinstance(node.condition, ast.GraineBooleanNode)
        assert node.condition.value is True
        assert isinstance(node.then_branch, ast.GraineNumberNode)
        assert node.then_branch.value == 1.0
        assert node.else_branch is not None
        assert isinstance(node.else_branch, ast.GraineNumberNode)
        assert node.else_branch.value == 2.0

    def test_conditional_node_without_else(self):
        """Test creating a conditional node without else branch."""
        condition = ast.GraineBooleanNode(value=True)
        then_branch = ast.GraineNumberNode(value=1.0)
        node = ast.GraineConditionalNode(condition=condition, then_branch=then_branch)
        assert node.else_branch is None

    def test_construction_node(self):
        """Test creating a class instantiation node."""
        arg = ast.GraineNumberNode(value=42.0)
        node = ast.GraineConstructionNode(class_name="MyClass", arguments=[arg])
        assert node.class_name == "MyClass"
        assert len(node.arguments) == 1


class TestStatementNodes:
    """Tests for statement AST nodes."""

    def test_let_node(self):
        """Test creating a let statement node."""
        identifier = ast.GraineIdentifierNode(name="x")
        value = ast.GraineNumberNode(value=42.0)
        node = ast.GraineLetNode(identifier=identifier, value=value)
        assert node.identifier.name == "x"
        # Type narrowing for value
        assert isinstance(node.value, ast.GraineNumberNode)
        assert node.value.value == 42.0

    def test_assign_node(self):
        """Test creating an assignment node."""
        identifier = ast.GraineIdentifierNode(name="x")
        value = ast.GraineNumberNode(value=10.0)
        node = ast.GraineAssignNode(identifier=identifier, value=value)
        # Type narrowing
        assert isinstance(node.identifier, ast.GraineIdentifierNode)
        assert node.identifier.name == "x"
        assert isinstance(node.value, ast.GraineNumberNode)
        assert node.value.value == 10.0

    def test_return_node(self):
        """Test creating a return statement node."""
        value = ast.GraineNumberNode(value=42.0)
        node = ast.GraineReturnNode(value=value)
        # Type narrowing
        assert isinstance(node.value, ast.GraineNumberNode)
        assert node.value.value == 42.0

    def test_block_node_empty(self):
        """Test creating an empty block node."""
        node = ast.GraineBlockNode()
        assert node.statements == []

    def test_block_node_emit(self):
        """Test emitting statements to a block using emit_statement function."""
        from fleur.dsl.jit import emit_statement

        block = ast.GraineBlockNode()
        stmt1 = ast.GraineLetNode(identifier=ast.GraineIdentifierNode(name="x"), value=ast.GraineNumberNode(value=1.0))
        stmt2 = ast.GraineLetNode(identifier=ast.GraineIdentifierNode(name="y"), value=ast.GraineNumberNode(value=2.0))
        emit_statement(block, stmt1, stmt2)
        assert len(block.statements) == 2

    def test_block_new_identifier(self):
        """Test generating new identifiers using new_identifier function."""
        from fleur.dsl.jit import new_identifier

        # new_identifier uses a global counter, so we need to call it within a context
        # For this test, we just verify that two calls produce different identifiers
        id1 = new_identifier()
        id2 = new_identifier()
        # With global counter, these should be sequential
        assert id1.name.startswith("_v_")
        assert id2.name.startswith("_v_")
        assert id1.name != id2.name

    def test_function_node(self):
        """Test creating a function node."""
        param1 = ast.GraineIdentifierNode(name="a")
        param2 = ast.GraineIdentifierNode(name="b")
        body = ast.GraineBlockNode()
        node = ast.GraineFunctionNode(name="add", parameters=[param1, param2], body=body)
        assert node.name == "add"
        assert len(node.parameters) == 2
        assert node.parameters[0].name == "a"

    def test_class_node_minimal(self):
        """Test creating a minimal class node."""
        node = ast.GraineClassNode(name="MyClass")
        assert node.name == "MyClass"
        assert node.constructor is None
        assert node.methods == []

    def test_class_node_with_constructor(self):
        """Test creating a class node with constructor."""
        constructor = ast.GraineFunctionNode(name="constructor")
        node = ast.GraineClassNode(name="MyClass", constructor=constructor)
        assert node.constructor is not None
        assert node.constructor.name == "constructor"

    def test_method_node_regular(self):
        """Test creating a regular method node."""
        func = ast.GraineFunctionNode(name="myMethod")
        node = ast.GraineMethodNode(name="myMethod", function=func)
        assert node.name == "myMethod"
        assert node.accessor is None

    def test_method_node_getter(self):
        """Test creating a getter method node."""
        func = ast.GraineFunctionNode(name="value")
        node = ast.GraineMethodNode(name="value", function=func, accessor="get")
        assert node.accessor == "get"

    def test_method_node_setter(self):
        """Test creating a setter method node."""
        func = ast.GraineFunctionNode(name="value")
        node = ast.GraineMethodNode(name="value", function=func, accessor="set")
        assert node.accessor == "set"

    def test_for_of_node(self):
        """Test creating a for-of loop node."""
        variable = ast.GraineIdentifierNode(name="item")
        # Create an identifier with explicit array type for the iterator
        iterator: ast.GraineASTExpr[ast.GraineArrayType] = ast.GraineIdentifierNode(name="items")
        body = ast.GraineBlockNode()
        node = ast.GraineForOfNode(variable=variable, iterator=iterator, body=body)
        assert node.variable.name == "item"
        # Type narrowing for iterator
        assert isinstance(node.iterator, ast.GraineIdentifierNode)
        assert node.iterator.name == "items"

    def test_if_node_without_else(self):
        """Test creating an if statement without else."""
        condition = ast.GraineBooleanNode(value=True)
        then_branch = ast.GraineBlockNode()
        node = ast.GraineIfNode(condition=condition, then_branch=then_branch)
        assert node.else_branch is None

    def test_if_node_with_else(self):
        """Test creating an if statement with else."""
        condition = ast.GraineBooleanNode(value=True)
        then_branch = ast.GraineBlockNode()
        else_branch = ast.GraineBlockNode()
        node = ast.GraineIfNode(condition=condition, then_branch=then_branch, else_branch=else_branch)
        assert node.else_branch is not None
