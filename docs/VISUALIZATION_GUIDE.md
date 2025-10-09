# Tumor Nanobot Simulation - Visualization Guide

## 🎨 Enhanced Visualization Features

The tumor simulation now features a comprehensive, intuitive visualization that clearly shows all aspects of the nanobot treatment simulation.

---

## 🎯 Key Visual Elements

### 1. **Tumor Boundary (Red Circle)**
The most prominent feature - a **thick red circle** marks the tumor boundary.

- **Location**: Center of the simulation domain
- **Size**: Configurable via `tumor_radius` parameter
- **Color**: Bright red (#ef4444) with 3px stroke
- **Purpose**: Clearly delineates where the cancer is

### 2. **Tumor Zones (Concentric Circles)**

The tumor has **three distinct zones** from center outward:

#### **Necrotic Core** (Center - Gray)
- **Appearance**: Dark gray circular region
- **Size**: 25% of tumor radius
- **Meaning**: Dead tissue from lack of blood supply
- **Why it matters**: No oxygen here, cells are already dead

#### **Hypoxic Zone** (Middle - Purple Tint)
- **Appearance**: Purple-tinted ring
- **Size**: 70% of tumor radius  
- **Meaning**: Low oxygen (< 5 mmHg), cells struggling to survive
- **Why it matters**: **Prime target for nanobots!** These cells are alive but vulnerable

#### **Viable Tumor** (Outer - Light Red Tint)
- **Appearance**: Light red background
- **Size**: Full tumor radius
- **Meaning**: Well-oxygenated cancer cells near blood vessels
- **Why it matters**: Harder to kill, but still targets

### 3. **Blood Vessels** (Pulsing Green Circles)

**The most important feature for understanding nanobot behavior!**

- **Appearance**: Large green circles with **pulsing animation**
- **Glow effect**: Animated pulsing from 30%-50% opacity
- **Supply radius**: Faded green halo showing oxygen/drug reach (~50 µm)
- **Label** (Detailed Mode): "O₂+Drug" text below vessel
- **Purpose**: 
  - Source of oxygen (keeps nearby cells viable)
  - Source of drug payload (where nanobots reload)
  - "Home base" for nanobots

**Why they pulse:**
The pulsing animation helps you immediately identify where nanobots go to reload!

### 4. **Nanobots** (Colored Circles with Indicators)

**Enhanced rendering with multiple visual cues:**

#### **Size & Structure:**
- Outer circle: 7px radius (larger than before)
- White border: 2px for definition
- Glow effect: 8px shadow blur
- Inner circle: Varies by drug payload

#### **Color by State:**
- **Gray** (?): Searching for targets
- **Yellow** (→): Targeting a hypoxic cell
- **Green** (💊): Actively delivering drug
- **Blue** (←): Returning to vessel
- **Purple** (⚡): Reloading at vessel

#### **Drug Payload Indicator:**
- Inner circle fills proportionally to payload
- **Blue inner circle**: >50% full
- **Red inner circle**: <50% full (running low)
- **No inner circle**: Empty (needs reload)

#### **LLM Indicator:**
- **Gold ring** (10px radius) around LLM-controlled nanobots
- Distinguishes AI-guided from rule-based

#### **Direction Markers** (Detailed Mode Only):
- Small symbols show current activity:
  - `?` - Searching
  - `→` - Moving toward target
  - `💊` - Delivering
  - `←` - Returning
  - `⚡` - Reloading

### 5. **Tumor Cells** (Small Colored Dots)

**Color-coded by cell phase:**

- **Red**: Viable (healthy cancer cells)
- **Purple**: Hypoxic (low oxygen, prime targets)
- **Gray**: Necrotic (naturally dead)
- **Yellow**: Apoptotic (killed by drug - SUCCESS!)

**Note**: If >200 cells, automatically sampled for performance

### 6. **Substrate Heatmaps** (Background Layer)

**Semi-transparent overlays** showing chemical concentrations:

#### **Opacity:**
- **Simple Mode**: 25% opacity (entities clearly visible)
- **Detailed Mode**: 40% opacity (see gradients better)

#### **Color Schemes:**

**Oxygen** (Blue → Red):
- **Blue regions**: Low oxygen (hypoxic, <5 mmHg)
- **Red regions**: Normal oxygen (normoxic, ~38 mmHg)
- **Where nanobots should go**: Blue regions!

**Drug** (Green Gradient):
- **Darker green**: Higher drug concentration
- **Light/no green**: No drug yet
- **Shows treatment coverage**: Where drugs have been delivered

**Trail Pheromone** (Emerald Green):
- **Bright emerald**: Successful delivery paths
- **Shows learning**: Nanobots mark good routes

**Alarm Pheromone** (Red):
- **Red areas**: Problems reported (API errors, navigation failures)
- **Helps swarm**: Avoid these areas

**Recruitment Pheromone** (Blue):
- **Blue areas**: Large hypoxic zones needing more nanobots
- **Coordination signal**: "Send help here!"

---

## 🎛️ Visualization Modes

### **Simple Mode (👤 Normie Mode)**

**Best for**: General understanding, presentations, demos

**What you see:**
- ✅ Tumor boundary (prominent red circle)
- ✅ Tumor zones (visible but subtle)
- ✅ Pulsing blood vessels (very clear)
- ✅ Nanobots (large, color-coded by state)
- ✅ Substrate heatmap (25% opacity, doesn't obscure entities)
- ❌ Zone labels
- ❌ Nanobot trails
- ❌ Direction markers
- ❌ Vessel labels

**Advantages:**
- Clean, uncluttered view
- Easy to understand at a glance
- Entities stand out clearly
- Perfect for non-technical audiences

### **Detailed Mode (🔬 Geek Mode)**

**Best for**: Research, analysis, debugging, technical presentations

**What you see:**
- ✅ Everything from Simple Mode
- ✅ **Zone labels**: Text annotations for tumor regions
- ✅ **Nanobot movement trails**: Dotted lines showing last 10 positions
- ✅ **Direction markers**: Symbols (?, →, 💊, ←, ⚡) on nanobots
- ✅ **Vessel labels**: "O₂+Drug" text below each vessel
- ✅ **Higher heatmap opacity**: 40% for better gradient visibility

**Advantages:**
- Maximum information density
- See exact nanobot paths
- Understand navigation decisions
- Identify successful strategies

**Toggle between modes** anytime during playback!

---

## 📊 Substrate Tab Guide

### **When to Use Each Substrate View:**

#### **Oxygen** (Recommended First View)
- See hypoxic tumor regions (blue = low O₂)
- Understand where nanobots should target
- Watch oxygen gradients from vessels
- **Best for**: Understanding tumor biology

#### **Drug** 
- See treatment coverage
- Identify under-treated regions
- Watch drug diffusion from delivery points
- **Best for**: Assessing treatment effectiveness

#### **Trail**
- See successful nanobot paths
- Identify efficient routes to tumor
- Watch swarm learning patterns
- **Best for**: Understanding pheromone communication

#### **Alarm**
- See problem areas
- Identify navigation challenges
- Spot API errors or dead ends
- **Best for**: Debugging and optimization

#### **Recruitment**
- See where help is needed
- Identify large hypoxic zones
- Watch swarm coordination
- **Best for**: Analyzing swarm behavior

---

## 🎬 Understanding Nanobot Behavior

### **The Full Cycle:**

1. **Start** → Nanobot spawns near a **pulsing green vessel** (fully loaded, blue inner circle)

2. **Search** → Gray color, moves using chemotaxis toward:
   - Low oxygen gradients (hypoxic tumor)
   - Trail pheromones (from successful peers)
   - Away from alarm pheromones

3. **Target** → Yellow color, locked onto specific hypoxic cell, moving directly toward it (→ marker)

4. **Deliver** → Green color, releasing drug payload (💊 marker), inner circle shrinking

5. **Return** → Blue color, navigating back to nearest vessel (← marker), inner circle now red (low payload)

6. **Reload** → Purple color, at vessel, refilling (⚡ marker), inner circle filling back to blue

7. **Repeat** → Cycle continues!

### **Watch For:**

✨ **Pulsing vessels** = "Reload stations"  
✨ **Yellow→Green transitions** = Successful delivery  
✨ **Emerald trails** = "Memory" of good paths  
✨ **Purple hypoxic regions** = Main targets  
✨ **Yellow tumor cells** = Treatment success!  

---

## 🔍 What to Look For

### **Successful Simulation:**

✅ Nanobots cluster around hypoxic zones (purple tint)  
✅ Green delivery markers appear near purple cells  
✅ Drug heatmap (green) spreads through tumor  
✅ Apoptotic cells (yellow) increase over time  
✅ Hypoxic cells decrease as treatment works  
✅ Emerald trails form stable paths  
✅ Nanobots efficiently cycle: vessel → tumor → vessel  

### **Problematic Behaviors:**

⚠️ Nanobots stuck outside tumor  
⚠️ All nanobots at vessels (not delivering)  
⚠️ Red alarm pheromones accumulating  
⚠️ No yellow (apoptotic) cells after many steps  
⚠️ Drug not reaching hypoxic zones  

---

## 💡 Pro Tips

### **For Best Visualization:**

1. **Start in Simple Mode** - Get the big picture
2. **Switch to Oxygen tab** - See where targets are (blue regions)
3. **Watch vessel pulsing** - Understand reload locations
4. **Switch to Drug tab** - See treatment progress
5. **Enable Detailed Mode** - Analyze specific behaviors
6. **Switch to Trail tab** - See swarm learning

### **For Presentations:**

- Use **Simple Mode** for clean, professional look
- Start with **Oxygen tab** to explain biology
- Switch to **Drug tab** to show treatment
- Pause on key moments (first kill, full coverage)
- Point out **pulsing vessels** as "drug depots"

### **For Research:**

- Use **Detailed Mode** for all data
- Compare **Trail vs Alarm** tabs to see learning
- Watch specific nanobots (gold ring = LLM)
- Export metrics from charts
- Note relationships between gradients and behavior

---

## 🎨 Color Reference

### **Core Colors:**

| Element | Color | Hex | Meaning |
|---------|-------|-----|---------|
| Tumor Boundary | Red | #ef4444 | Cancer zone |
| Blood Vessels | Green | #10b981 | O₂ + Drug source |
| Nanobot - Searching | Gray | #6b7280 | Looking for targets |
| Nanobot - Targeting | Yellow | #fbbf24 | Locked on target |
| Nanobot - Delivering | Green | #10b981 | Releasing drug |
| Nanobot - Returning | Blue | #3b82f6 | Going to vessel |
| Nanobot - Reloading | Purple | #8b5cf6 | Refilling payload |
| Viable Cells | Red | #ef4444 | Healthy cancer |
| Hypoxic Cells | Purple | #a855f7 | Low oxygen (targets!) |
| Necrotic Cells | Gray | #6b7280 | Naturally dead |
| Apoptotic Cells | Yellow | #fbbf24 | Drug-killed (success!) |

---

## 📐 Scale and Dimensions

### **Default Setup:**
- **Domain**: 600 × 600 µm (0.6 × 0.6 mm)
- **Tumor**: 200 µm radius (0.2 mm)
- **Vessels**: 8-10 around periphery
- **Vessel range**: 50 µm (shown as faded green halo)
- **Nanobots**: 5-10 agents

### **Size Comparisons:**
- **Human cell**: ~10 µm diameter
- **Tumor radius**: ~200 µm = 20 cells across
- **Vessel spacing**: ~100 µm = 10 cells
- **Nanobot size**: Microscopic (~100 nm in reality, scaled up for visibility)

---

## 🚀 Quick Visual Checklist

Before presenting or analyzing, verify:

- [ ] Tumor boundary is clearly visible (red circle)
- [ ] Blood vessels are pulsing (animation working)
- [ ] Nanobots have different colors (states are rendering)
- [ ] Substrate heatmap is visible but not overwhelming
- [ ] Legend boxes are visible below canvas
- [ ] Simple/Detailed mode toggle works
- [ ] All 5 substrate tabs switch properly

---

## 🆘 Visual Troubleshooting

### **"I can't see the tumor!"**
- ✅ Fixed! Tumor now has prominent **red boundary circle**
- Still not seeing it? Check that `tumor_radius` < `domain_size` / 2

### **"Vessels blend into background"**
- ✅ Fixed! Vessels now **pulse** and have **glow effects**
- Much larger (8px radius vs 4px before)
- Try switching to Oxygen tab to see their oxygen supply radius

### **"Too many things on screen"**
- ✅ Use **Simple Mode** (👤) - reduces visual clutter
- ✅ Substrate opacity reduced to 25% in Simple Mode
- ✅ Zone labels and trails hidden in Simple Mode

### **"Can't tell what nanobots are doing"**
- ✅ Each state now has **distinct color**
- ✅ Added glow effects for prominence
- ✅ Detailed Mode shows **direction markers** (?, →, 💊, ←, ⚡)
- ✅ Detailed Mode shows **movement trails** (last 10 positions)

### **"Substrate heatmaps hide everything"**
- ✅ Opacity reduced from 50-80% to **25-40%**
- ✅ Entities rendered **on top** of substrates
- ✅ Borders and glows help entities stand out

---

## 🎓 Educational Use

### **For Teaching:**

1. **Start Simple:**
   - Simple Mode + Oxygen tab
   - Point out: "Red circle = tumor, Green = blood vessels"
   - "Watch nanobots (colored dots) move from green vessels to purple hypoxic zones"

2. **Show Treatment:**
   - Switch to Drug tab
   - "Green areas = where nanobots delivered medicine"
   - "Yellow cells = cancer cells that died from treatment"

3. **Explain Learning:**
   - Switch to Trail tab (Detailed Mode)
   - "Emerald trails = nanobots remembering successful paths"
   - "Like ants leaving pheromone trails!"

### **For Research:**

1. **Hypothesis Testing:**
   - Compare pheromone vs non-pheromone strategies
   - Measure delivery efficiency
   - Analyze coverage patterns

2. **Parameter Optimization:**
   - Tune nanobot count
   - Adjust chemotaxis weights
   - Optimize swarm behavior

3. **Visual Analysis:**
   - Identify navigation patterns
   - Spot inefficiencies
   - Find optimal strategies

---

## 📸 Screenshot Tips

### **Best Views for Documentation:**

1. **Overview Shot**: Simple Mode + Oxygen tab
   - Shows full simulation state
   - Tumor clearly visible
   - Clean and professional

2. **Action Shot**: Detailed Mode + Drug tab + mid-simulation
   - Nanobots actively delivering
   - Some cells turning yellow (killed)
   - Drug spreading through tumor

3. **Learning Shot**: Detailed Mode + Trail tab + late simulation
   - Clear emerald trails formed
   - Shows swarm intelligence in action

4. **Results Shot**: Any mode + final step
   - Many yellow cells (successful treatment)
   - Reduced hypoxic region
   - Good drug coverage

---

## 🔧 Customization Guide

### **Want to change colors?**

Edit `TumorSimulationGrid.tsx`:
```typescript
// Line ~161: Substrate colors
case "oxygen":
  color = `rgba(...)`;  // Modify RGB values

// Line ~326: Nanobot state colors
case "targeting":
  outerColor = "#fbbf24";  // Change hex code
```

### **Want bigger/smaller entities?**

```typescript
// Blood vessels: Line ~234
ctx.arc(x, y, 8, 0, Math.PI * 2);  // Change radius (currently 8)

// Nanobots: Line ~357
ctx.arc(x, y, 7, 0, Math.PI * 2);  // Change radius (currently 7)

// Tumor cells: Line ~280
ctx.arc(x, y, 3, 0, Math.PI * 2);  // Change radius (currently 3)
```

### **Want different pulsing speed?**

```typescript
// Line ~59: Pulse animation
setInterval(() => {
  setPulsePhase(prev => (prev + 0.1) % (Math.PI * 2));
}, 50);  // Change interval (currently 50ms)
```

---

## 🎬 Animation Features

### **Automatic Animations:**

1. **Vessel Pulsing** (Always on)
   - Sine wave animation (0.1 rad/frame)
   - Helps identify oxygen sources
   - Eye-catching and informative

2. **Nanobot Trails** (Detailed Mode)
   - Tracks last 10 positions
   - Dotted blue lines
   - Shows navigation patterns

3. **Glow Effects**
   - Nanobots have 8px shadow blur
   - Color matches state
   - Makes them pop visually

---

## 🌟 What Makes This Visualization Unique

### **Compared to Standard PhysiCell Visualizations:**

✅ **Real-time playback** (not just static snapshots)  
✅ **Interactive substrate switching** (5 views in one)  
✅ **Simple/Detailed mode toggle** (accessibility!)  
✅ **Pulsing animations** (not static)  
✅ **Movement trails** (see navigation patterns)  
✅ **State-based coloring** (understand what nanobots are doing)  
✅ **Comprehensive legend** (self-documenting)  

### **Compared to Other Tumor Simulations:**

✅ **Swarm intelligence focus** (not single-agent)  
✅ **Pheromone communication** (unique feature!)  
✅ **LLM integration** (AI-guided treatment)  
✅ **Blockchain logging** (reproducible science)  
✅ **Web-based** (no installation needed)  

---

## 📱 Responsive Design

The visualization adapts to screen size:

- **Canvas size**: `Math.min(window.innerWidth * 0.6, 800)`
- **Maximum**: 800×800 pixels
- **On smaller screens**: Automatically scales down
- **Legend**: Responsive grid layout (3 cols → 2 cols → 1 col)

---

## ✨ Summary

**The enhanced visualization makes it crystal clear:**

1. **Where the tumor is** → Bright red boundary circle
2. **Where nanobots reload** → Pulsing green vessels
3. **What nanobots are doing** → Color-coded states
4. **How much drug they have** → Inner circle color
5. **Where treatment is working** → Yellow (killed) cells
6. **What the swarm learned** → Emerald trail pheromones

**Two modes for two audiences:**
- **Simple Mode**: Clean, professional, easy to understand
- **Detailed Mode**: All the data, all the details, for geeks!

---

**The simulation is now visually intuitive and scientifically accurate!** 🎉

