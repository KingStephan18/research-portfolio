"""Local authorization-decision demonstration, not an execution sandbox.

The caller supplies authenticated principal, trusted policy, clock, revocations
and approvals separately from the untrusted proposed action. This module does
not authenticate that caller, sign grants, execute tools or persist decisions.
"""
from __future__ import annotations
import re
from typing import Any

ACTIONS=frozenset({'read','write','publish','delete'})
SENSITIVE=frozenset({'publish','delete'})
IDENTIFIER=re.compile(r'[a-z0-9][a-z0-9_-]{0,63}\Z')
RESOURCE=re.compile(r'artifact:[a-z0-9][a-z0-9_-]{0,63}/[a-z0-9][a-z0-9_-]{0,63}\Z')

def _identifier(value: Any) -> bool:
    return isinstance(value,str) and bool(IDENTIFIER.fullmatch(value))

def _resource(value: Any) -> bool:
    # The lab uses opaque canonical IDs, not filesystem paths or URLs.
    return isinstance(value,str) and bool(RESOURCE.fullmatch(value))

def _binding(value: Any, *, grant: bool) -> bool:
    if not isinstance(value,dict): return False
    if grant and not _identifier(value.get('id')): return False
    return (_identifier(value.get('principal'))
            and isinstance(value.get('action'),str) and value['action'] in ACTIONS
            and _resource(value.get('resource'))
            and type(value.get('expires_at')) is int and value['expires_at'] >= 0)

def _result(allowed: bool, reason: str) -> dict[str, Any]:
    return {'allowed':allowed,'reason':reason}

def authorize(request: Any, *, principal: str, grants: list[dict],
              revoked: Any, approvals: list[dict], now: int) -> dict[str, Any]:
    """Fail closed unless an exact, live grant and necessary approval exist.

    Extra request fields, including an apparent role/approval/instruction, never
    become authority. Returned ALLOW is only a decision on supplied context.
    A real executor must bind the decision and execution to the same operation
    and policy version, avoid races, and enforce approval consumption itself.
    """
    if not _identifier(principal) or type(now) is not int or now < 0:
        return _result(False,'INVALID_TRUSTED_CONTEXT')
    if not isinstance(grants,list) or not all(_binding(g,grant=True) for g in grants):
        return _result(False,'INVALID_TRUSTED_CONTEXT')
    if len({g['id'] for g in grants}) != len(grants):
        return _result(False,'INVALID_TRUSTED_CONTEXT')
    if not isinstance(revoked,(list,tuple,set,frozenset)) or not all(_identifier(i) for i in revoked):
        return _result(False,'INVALID_TRUSTED_CONTEXT')
    if not isinstance(approvals,list) or not all(_binding(a,grant=False) for a in approvals):
        return _result(False,'INVALID_TRUSTED_CONTEXT')
    if not isinstance(request,dict) or not isinstance(request.get('action'),str):
        return _result(False,'MALFORMED_REQUEST')
    action=request['action']; resource=request.get('resource')
    if action not in ACTIONS: return _result(False,'UNSUPPORTED_ACTION')
    if not _resource(resource): return _result(False,'NONCANONICAL_RESOURCE')
    matching=[g for g in grants if g['principal']==principal
              and g['action']==action and g['resource']==resource]
    if not matching: return _result(False,'SCOPE_MISMATCH')
    live=[g for g in matching if g['id'] not in revoked and now < g['expires_at']]
    if not live: return _result(False,'REVOKED_OR_EXPIRED')
    if action in SENSITIVE and not any(
        a['principal']==principal and a['action']==action and a['resource']==resource
        and now < a['expires_at'] for a in approvals
    ):
        return _result(False,'APPROVAL_REQUIRED')
    return _result(True,'ALLOW')


def action_only_baseline(request: Any, *, principal: str, grants: list[dict],
                         revoked: Any, approvals: list[dict], now: int) -> bool:
    """Intentionally incomplete teaching baseline, NOT recommended code.

    Ignores resource, expiry, revocation and approval. Included to make each
    omitted check observable, not to represent a commercial product or model.
    """
    if not isinstance(request,dict) or not isinstance(grants,list): return False
    return any(isinstance(g,dict) and g.get('principal')==principal
               and g.get('action')==request.get('action') for g in grants)
