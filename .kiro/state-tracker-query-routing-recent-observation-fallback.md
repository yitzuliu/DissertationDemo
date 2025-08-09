## State Tracker Query Routing – Recent Observation Aware Fallback

Status: **Enhanced Technical Specification** (Ready for Implementation)
Owners: State Tracker / Query Processor / VLM Fallback
Last updated: 2025-08-08
Version: 2.0

### 📋 Executive Summary

This specification defines a critical enhancement to the State Tracker's query routing system that addresses stale template responses during scene transitions. By implementing recent-observation-aware fallback logic, the system will intelligently route queries to VLM fallback when the current state appears stale based on recent visual observations.

**Key Benefits:**
- 🎯 **Eliminates stale responses** during scene transitions
- ⚡ **Maintains responsiveness** for valid states
- 🛡️ **Preserves existing fallback logic** without disruption
- 📊 **Configurable TTL** for fine-tuned behavior

### 🚨 Why we need this change

**Observed Issue:** When users switch scenes but the `current_state` hasn't been updated yet, task-related queries (e.g., "What step am I on?") may return stale template responses from the previous task's step. This occurs because current query routing only considers:

- Query classification confidence (static 0.40 threshold)
- Presence of `current_state` and step data

**Missing Consideration:** The system doesn't evaluate whether recent visual observations indicate:
- Scene inconsistency (repeated LOW confidence observations)
- Stale state data (no recent successful updates within TTL)

**Impact:**
- ❌ Short windows after scene changes surface stale answers
- ❌ Reduces user trust in system accuracy
- ❌ Creates confusion about current task status

### 🎯 What scenario this fixes

**Problem Scenario:**
```
User changes scene → VLM observations become LOW 
→ User asks "Where am I?" 
→ Current logic returns old step (stale template response)
```

**Solution Scenario:**
```
User changes scene → VLM observations become LOW 
→ User asks "Where am I?" 
→ System detects stale state → Routes to VLM fallback
→ Fresh, accurate response based on current scene
```

### 🏗️ What we will change (high level)

**New Rule:** Add recent-observation-aware logic to query routing:
- **Trigger Condition:** Recent observation confidence is LOW OR time since last HIGH/MEDIUM update exceeds TTL
- **Action:** Force VLM fallback instead of using stale `current_state` template
- **Preservation:** All existing fallback rules remain unchanged

**Complementary Behavior:**
- LOW confidence observations → Always route to VLM fallback
- HIGH confidence (≥0.65) → Immediate state updates
- MEDIUM confidence → Follow existing thin-guard rules

### 🔧 Detailed Technical Design

#### 1. State Tracker Enhancement: Recent Observation Status API

**New Method:** `get_recent_observation_status()`

```python
@dataclass
class RecentObservationStatus:
    """Status of recent observations for fallback decision making"""
    seconds_since_last_update: Optional[float]  # None if no state
    last_observation_confidence_level: ConfidenceLevel
    consecutive_low_count: int
    seconds_since_last_observation: Optional[float]  # None if no observations
    last_observation_timestamp: Optional[datetime]
    current_state_timestamp: Optional[datetime]
    fallback_recommended: bool  # Computed recommendation

def get_recent_observation_status(self, fallback_ttl_seconds: float = 15.0) -> RecentObservationStatus:
    """
    Get recent observation status for fallback decision making.
    
    Args:
        fallback_ttl_seconds: TTL threshold for considering state stale
        
    Returns:
        RecentObservationStatus with computed fallback recommendation
    """
```

**Implementation Details:**
- **Data Sources:** `current_state.timestamp`, `processing_metrics[-1]`, `consecutive_low_count`
- **Performance:** O(1) operation using existing data structures
- **Thread Safety:** Read-only access to existing state

#### 2. Query Processor Enhancement: Recent Observation Aware Fallback

**Enhanced Method:** `_should_use_vlm_fallback()`

```python
def _should_use_vlm_fallback(self, query_type: QueryType, current_state: Optional[Dict[str, Any]], 
                            confidence: float, state_tracker=None) -> bool:
    """
    Enhanced fallback decision with recent observation awareness.
    
    Args:
        query_type: Classified query type
        current_state: Current state data
        confidence: Classification confidence
        state_tracker: Optional state tracker instance for recent observation check
        
    Returns:
        True if VLM fallback should be used
    """
    # Existing fallback rules (unchanged)
    if not (self.enhanced_vlm_fallback or self.vlm_fallback):
        return False
    
    if not current_state:
        return True
    
    if confidence < 0.40:
        return True
    
    if query_type == QueryType.UNKNOWN:
        return True
    
    if not current_state.get('step_index') and not current_state.get('matched_step'):
        return True
    
    # NEW: Recent observation aware fallback
    if state_tracker and self._should_fallback_due_to_recent_observations(state_tracker):
        return True
    
    return False

def _should_fallback_due_to_recent_observations(self, state_tracker, 
                                               fallback_ttl_seconds: float = 15.0) -> bool:
    """
    Check if fallback should be used based on recent observations.
    
    Args:
        state_tracker: State tracker instance
        fallback_ttl_seconds: TTL threshold for stale state detection
        
    Returns:
        True if recent observations suggest fallback is needed
    """
    try:
        status = state_tracker.get_recent_observation_status(fallback_ttl_seconds)
        return status.fallback_recommended
    except Exception as e:
        logger.warning(f"Error checking recent observation status: {e}")
        return False  # Default to existing behavior on error
```

#### 3. Integration Pattern

**Query Processor Integration:**
```python
def process_query(self, query: str, current_state: Optional[Dict[str, Any]], 
                 query_id: str = None, log_manager = None, state_tracker = None) -> QueryResult:
    """
    Enhanced query processing with recent observation awareness.
    """
    # ... existing classification logic ...
    
    # Enhanced fallback decision
    should_use_fallback = self._should_use_vlm_fallback(
        query_type, current_state, confidence, state_tracker
    )
    
    # ... rest of processing logic ...
```

**State Tracker Integration:**
```python
def process_instant_query(self, query: str, query_id: str = None, request_id: str = None):
    """
    Enhanced instant query processing with self-reference for fallback.
    """
    # ... existing logic ...
    
    # Pass self as state_tracker for recent observation check
    result = self.query_processor.process_query(
        query, current_state, query_id, self.log_manager, self
    )
    
    # ... rest of processing logic ...
```

### ⚙️ Configuration Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `fallback_ttl_seconds` | 15.0 | 5.0 - 30.0 | TTL for considering state stale |
| `high_confidence_threshold` | 0.65 | 0.60 - 0.80 | High confidence threshold |
| `medium_confidence_threshold` | 0.40 | 0.35 - 0.50 | Medium confidence threshold |
| `feature_flag_enabled` | True | Boolean | Enable/disable feature |

**Configuration File:** `src/config/state_tracker_config.json`
```json
{
  "recent_observation_fallback": {
    "enabled": true,
    "fallback_ttl_seconds": 15.0,
    "high_confidence_threshold": 0.65,
    "medium_confidence_threshold": 0.40
  }
}
```

### ✅ Acceptance Criteria

#### Functional Requirements
1. **Scene Transition Detection:**
   - When scene is switched and recent observations are LOW, queries like "Where am I?" route to VLM fallback
   - No stale template answers during transition windows

2. **State Recovery:**
   - When user returns to original scene and HIGH/MEDIUM observations occur, template answers resume immediately
   - Seamless transition back to template responses

3. **Existing Behavior Preservation:**
   - No regressions in existing fallback rules
   - All current query types continue to work as expected

#### Performance Requirements
1. **Response Time:**
   - Recent observation check adds <5ms to query processing
   - Template responses remain <50ms
   - VLM fallback responses remain 1-5 seconds

2. **Memory Usage:**
   - No additional memory overhead for recent observation tracking
   - Uses existing data structures and metrics

#### Reliability Requirements
1. **Error Handling:**
   - Graceful degradation if recent observation check fails
   - Default to existing behavior on errors
   - Comprehensive logging for debugging

2. **Backward Compatibility:**
   - Feature can be disabled via configuration
   - Existing API contracts remain unchanged
   - No breaking changes to public interfaces

### 🧪 Comprehensive Test Plan

#### Unit Tests

**1. State Tracker Recent Observation Status Tests**
```python
def test_get_recent_observation_status_no_state():
    """Test status when no current state exists"""
    
def test_get_recent_observation_status_fresh_state():
    """Test status with recent HIGH confidence update"""
    
def test_get_recent_observation_status_stale_state():
    """Test status with old state and recent LOW observations"""
    
def test_get_recent_observation_status_mixed_observations():
    """Test status with mixed confidence observations"""
```

**2. Query Processor Fallback Decision Tests**
```python
def test_fallback_decision_with_recent_low_observations():
    """Test fallback when recent observations are LOW"""
    
def test_fallback_decision_with_stale_state():
    """Test fallback when state is older than TTL"""
    
def test_fallback_decision_with_fresh_high_confidence():
    """Test no fallback with recent HIGH confidence"""
    
def test_fallback_decision_error_handling():
    """Test graceful error handling in fallback decision"""
```

#### Integration Tests

**1. End-to-End Scene Transition Tests**
```python
def test_scene_switch_to_low_confidence():
    """Complete flow: scene switch → LOW observations → query → fallback"""
    
def test_scene_return_to_high_confidence():
    """Complete flow: return to scene → HIGH observations → query → template"""
    
def test_mixed_confidence_scenario():
    """Complex scenario with varying confidence levels"""
```

**2. Performance Tests**
```python
def test_recent_observation_check_performance():
    """Verify recent observation check adds <5ms overhead"""
    
def test_memory_usage_unchanged():
    """Verify no additional memory overhead"""
```

#### Edge Case Tests

**1. Boundary Conditions**
```python
def test_ttl_boundary_conditions():
    """Test behavior exactly at TTL boundaries"""
    
def test_empty_processing_metrics():
    """Test behavior with no processing metrics"""
    
def test_concurrent_access():
    """Test thread safety of recent observation checks"""
```

**2. Error Scenarios**
```python
def test_state_tracker_unavailable():
    """Test behavior when state tracker is None"""
    
def test_configuration_errors():
    """Test behavior with invalid configuration"""
    
def test_network_failures():
    """Test behavior during VLM fallback failures"""
```

### 🚀 Implementation Roadmap

#### Phase 1: Core Implementation (Week 1)
1. **State Tracker Enhancement**
   - Implement `get_recent_observation_status()` method
   - Add `RecentObservationStatus` dataclass
   - Add comprehensive unit tests

2. **Query Processor Enhancement**
   - Enhance `_should_use_vlm_fallback()` method
   - Add `_should_fallback_due_to_recent_observations()` method
   - Update `process_query()` signature

#### Phase 2: Integration & Testing (Week 2)
1. **Integration Implementation**
   - Update `process_instant_query()` to pass state tracker
   - Add configuration file support
   - Implement feature flag system

2. **Comprehensive Testing**
   - Run all unit and integration tests
   - Performance benchmarking
   - Edge case validation

#### Phase 3: Deployment & Monitoring (Week 3)
1. **Staging Deployment**
   - Deploy to staging environment
   - Enable feature flag
   - Monitor routing metrics

2. **Production Rollout**
   - Gradual rollout with monitoring
   - A/B testing if needed
   - Full deployment upon validation

### 📊 Monitoring & Metrics

#### Key Metrics to Track
1. **Fallback Trigger Rate:**
   - Percentage of queries routed to VLM fallback due to recent observations
   - Breakdown by confidence level and TTL triggers

2. **Response Quality:**
   - User satisfaction scores for fallback vs template responses
   - Accuracy metrics for fallback responses

3. **Performance Impact:**
   - Query processing time distribution
   - Memory usage trends
   - Error rates

#### Alerting Thresholds
- **High Fallback Rate:** >30% of queries using recent observation fallback
- **Performance Degradation:** >10ms increase in average query processing time
- **Error Rate:** >1% errors in recent observation checks

### 🛡️ Risk Assessment & Mitigations

#### High Risk
1. **Over-triggering Fallback**
   - **Risk:** TTL too small causing unnecessary VLM calls
   - **Mitigation:** Start with 15s, tune based on metrics
   - **Monitoring:** Track fallback trigger rate vs user satisfaction

2. **Performance Impact**
   - **Risk:** Recent observation check adds significant overhead
   - **Mitigation:** Optimize implementation, use existing data structures
   - **Monitoring:** Measure query processing time impact

#### Medium Risk
1. **Configuration Complexity**
   - **Risk:** Too many tunable parameters
   - **Mitigation:** Start with minimal config, add complexity gradually
   - **Monitoring:** Track configuration usage and effectiveness

2. **Error Propagation**
   - **Risk:** Recent observation check errors affect query processing
   - **Mitigation:** Comprehensive error handling with graceful degradation
   - **Monitoring:** Track error rates and types

#### Low Risk
1. **Backward Compatibility**
   - **Risk:** Breaking changes to existing APIs
   - **Mitigation:** Maintain existing interfaces, use feature flags
   - **Monitoring:** Verify all existing functionality works

### 🔄 Rollback Plan

#### Immediate Rollback (Feature Flag)
```python
# Disable feature via configuration
{
  "recent_observation_fallback": {
    "enabled": false
  }
}
```

#### Code Rollback (If Needed)
1. **Revert Query Processor Changes:**
   - Remove recent observation parameters from method signatures
   - Restore original `_should_use_vlm_fallback()` logic

2. **Revert State Tracker Changes:**
   - Remove `get_recent_observation_status()` method
   - Remove `RecentObservationStatus` dataclass

3. **Update Tests:**
   - Remove recent observation related tests
   - Restore original test expectations

### 📚 Documentation Updates

#### Code Documentation
- Update method docstrings with new parameters
- Add examples for recent observation usage
- Document configuration options

#### User Documentation
- Update State Tracker User Guide
- Add troubleshooting section for fallback behavior
- Document configuration tuning guidelines

#### API Documentation
- Update API reference with new endpoints
- Document new response fields
- Add migration guide for existing integrations

### 🎯 Success Metrics

#### Primary Success Metrics
1. **Stale Response Elimination:**
   - 95% reduction in stale template responses during scene transitions
   - User satisfaction improvement >20% for transition scenarios

2. **Performance Maintenance:**
   - Query processing time increase <5ms
   - Memory usage increase <1MB
   - Error rate <0.1%

#### Secondary Success Metrics
1. **System Reliability:**
   - 99.9% uptime during rollout
   - Zero breaking changes to existing functionality
   - Successful rollback capability

2. **User Experience:**
   - Improved response accuracy during scene changes
   - Maintained responsiveness for valid states
   - Seamless transition between template and fallback responses

### 📝 Implementation Checklist

#### Pre-Implementation
- [ ] Review and approve technical design
- [ ] Set up monitoring and alerting
- [ ] Prepare rollback plan
- [ ] Update test infrastructure

#### Implementation
- [ ] Implement State Tracker enhancements
- [ ] Implement Query Processor enhancements
- [ ] Add configuration support
- [ ] Write comprehensive tests
- [ ] Update documentation

#### Testing
- [ ] Run unit tests (100% pass rate)
- [ ] Run integration tests
- [ ] Performance benchmarking
- [ ] Edge case validation
- [ ] Security review

#### Deployment
- [ ] Staging deployment
- [ ] Feature flag testing
- [ ] Gradual production rollout
- [ ] Monitor key metrics
- [ ] Full deployment upon validation

### 🔮 Future Enhancements

#### Potential Improvements
1. **Adaptive TTL:** Dynamic TTL based on observation patterns
2. **Confidence Weighting:** Weight recent observations by confidence level
3. **Scene Change Detection:** Explicit scene change detection algorithms
4. **User Feedback Integration:** Learn from user corrections

#### Research Areas
1. **Machine Learning:** Predict optimal fallback timing
2. **Context Awareness:** Consider task complexity in fallback decisions
3. **Multi-Modal Integration:** Combine visual and audio observations

---

**Document Version:** 2.0  
**Last Updated:** 2025-08-08  
**Next Review:** 2025-08-15  
**Status:** Ready for Implementation


