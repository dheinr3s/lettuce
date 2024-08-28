from tests.conftest import *


def test_collision_optimizes_pseudo_entropy(fix_configuration,
                                            fix_stencil):
    """checks if the pseudo-entropy of the KBC collision model is at least
    higher than the BGK pseudo-entropy"""
    if type(fix_stencil) not in [D2Q9, D3Q27]:
        pytest.skip("KBCCollision only implemented for D2Q9 and D3Q27.")
    device, dtype, use_native = fix_configuration
    if use_native:
        pytest.skip("This test does not depend on the native implementation.")
    context = Context(device=device, dtype=dtype, use_native=False)
    flow = TestFlow(context=context,
                    resolution=[16] * fix_stencil.d,
                    reynolds_number=100,
                    mach_number=0.1,
                    stencil=fix_stencil)
    np.random.seed(1)  # arbitrary, but deterministic
    flow.f = flow.context.convert_to_tensor(np.random.random(
        [flow.stencil.q] + [3] * flow.stencil.d))
    tau = 0.5003
    coll_kbc = KBCCollision(tau)
    coll_bgk = BGKCollision(tau)
    f_kbc = coll_kbc(flow)
    f_bgk = coll_bgk(flow)
    entropy_kbc = flow.pseudo_entropy_local(f_kbc)
    entropy_bgk = flow.pseudo_entropy_local(f_bgk)
    assert (entropy_bgk < entropy_kbc).all()