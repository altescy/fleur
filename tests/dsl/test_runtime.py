"""Tests for the runtime context management."""

import pytest

from fleur.dsl.ir import IRBlock, IRLetStmt, IRLiteralNumberExpr
from fleur.dsl.runtime import require_block, use_block


class TestRuntimeContext:
    """Test runtime context management."""

    def test_use_block_creates_new_block(self):
        """Test that use_block creates a new block."""
        with use_block() as block:
            assert isinstance(block, IRBlock)
            assert block.body == []

    def test_require_block_within_use_block(self):
        """Test that require_block returns the current block."""
        with use_block() as block:
            current = require_block()
            assert current is block

    def test_require_block_returns_default_outside_context(self):
        """Test that require_block returns a default block outside use_block."""
        block = require_block()
        assert isinstance(block, IRBlock)

    def test_use_block_restores_previous_context(self):
        """Test that use_block restores the previous context after exiting."""
        outer_block = require_block()

        with use_block() as inner_block:
            assert require_block() is inner_block
            assert inner_block is not outer_block

        # After exiting, should be back to outer context
        assert require_block() is outer_block

    def test_nested_use_block(self):
        """Test nested use_block contexts."""
        with use_block() as outer:
            outer_current = require_block()
            assert outer_current is outer

            with use_block() as inner:
                inner_current = require_block()
                assert inner_current is inner
                assert inner is not outer

            # After inner exits, should be back to outer
            assert require_block() is outer

    def test_statements_emitted_to_correct_block(self):
        """Test that statements are emitted to the correct block."""
        with use_block() as outer:
            stmt1 = IRLetStmt(name="x", value=IRLiteralNumberExpr(1))
            outer.emit(stmt1)

            with use_block() as inner:
                stmt2 = IRLetStmt(name="y", value=IRLiteralNumberExpr(2))
                inner.emit(stmt2)

                # Inner block should only have stmt2
                assert len(inner.body) == 1
                assert inner.body[0] is stmt2

            # Outer block should only have stmt1
            assert len(outer.body) == 1
            assert outer.body[0] is stmt1

    def test_multiple_sequential_use_blocks(self):
        """Test multiple sequential use_block contexts."""
        with use_block() as block1:
            stmt1 = IRLetStmt(name="a", value=IRLiteralNumberExpr(1))
            block1.emit(stmt1)

        with use_block() as block2:
            stmt2 = IRLetStmt(name="b", value=IRLiteralNumberExpr(2))
            block2.emit(stmt2)

        # Blocks should be independent
        assert len(block1.body) == 1
        assert len(block2.body) == 1
        assert block1 is not block2

    def test_use_block_with_exception(self):
        """Test that use_block properly restores context even on exception."""
        outer_block = require_block()

        with pytest.raises(ValueError):
            with use_block() as inner:
                assert require_block() is inner
                raise ValueError("Test exception")

        # Should still restore to outer context
        assert require_block() is outer_block

    def test_deeply_nested_contexts(self):
        """Test deeply nested use_block contexts."""
        blocks = []

        with use_block() as b1:
            blocks.append(b1)
            with use_block() as b2:
                blocks.append(b2)
                with use_block() as b3:
                    blocks.append(b3)
                    current = require_block()
                    assert current is b3

                assert require_block() is b2
            assert require_block() is b1

        # All blocks should be different
        assert len(set(id(b) for b in blocks)) == 3
