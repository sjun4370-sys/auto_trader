/**
 * @author Jun
 */
import { useEffect, useRef, useState } from 'react'

interface RingConfig {
  id: number
  size: number
  x: number
  y: number
  speed: number
  rotateSpeed: number
  borderWidth: number
  borderColor: string
  translateX: number
  translateY: number
  opacity: number
  scale: number
  removing?: boolean
  appearing?: boolean
}

const MIN_RINGS = 10
const MAX_RINGS = 18

function BackgroundDecoration() {
  const [rings, setRings] = useState<RingConfig[]>([])
  const ringsRef = useRef<Map<number, HTMLDivElement>>(new Map())
  const ringIdRef = useRef(0)
  const rotationRef = useRef(0)

  const createRing = (existingRings: RingConfig[] = []): RingConfig => {
    const id = ringIdRef.current++
    const sizes = [100, 150, 180, 220, 280, 350]
    const size = sizes[Math.floor(Math.random() * sizes.length)]

    let x = Math.random() * 80 + 5
    let y = Math.random() * 80 + 5
    let attempts = 0
    while (attempts < 20) {
      const tooClose = existingRings.some(ring => {
        const dx = ring.x - x
        const dy = ring.y - y
        return Math.sqrt(dx * dx + dy * dy) < 20
      })
      if (!tooClose) break
      x = Math.random() * 80 + 5
      y = Math.random() * 80 + 5
      attempts++
    }

    const borderColors = [
      'rgba(255,255,255,0.1)',
      'rgba(255,255,255,0.12)',
      'rgba(255,255,255,0.15)',
      'rgba(255,255,255,0.08)',
      'rgba(255,255,255,0.18)',
    ]

    return {
      id,
      size,
      x,
      y,
      speed: 0.08 + Math.random() * 0.15,
      rotateSpeed: 15 + Math.random() * 25,
      borderWidth: Math.random() > 0.5 ? 2 : 1.5,
      borderColor: borderColors[Math.floor(Math.random() * borderColors.length)],
      translateX: 0,
      translateY: 0,
      opacity: 0,
      scale: 1,
      appearing: true,
    }
  }

  useEffect(() => {
    const initialRings: RingConfig[] = []
    for (let i = 0; i < 12; i++) {
      initialRings.push(createRing(initialRings))
    }
    setRings(initialRings)
  }, [])

  useEffect(() => {
    let animationFrameId: number

    const animate = () => {
      rotationRef.current += 0.02

      ringsRef.current.forEach((element, id) => {
        if (!element) return
        const ring = rings.find(r => r.id === id)
        if (!ring) return

        const rot = rotationRef.current * (ring.rotateSpeed / 40)
        const tx = ring.translateX
        const ty = ring.translateY + Math.sin(rotationRef.current * ring.speed) * 30

        element.style.transform = `translate(${tx}px, ${ty}px) rotate(${rot}deg) scale(${ring.scale})`
        element.style.opacity = String(ring.opacity)
      })

      animationFrameId = requestAnimationFrame(animate)
    }

    animationFrameId = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animationFrameId)
  }, [rings])

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      ringsRef.current.forEach((element, id) => {
        if (!element) return
        const ring = rings.find(r => r.id === id)
        if (!ring || ring.removing) return

        const rect = element.getBoundingClientRect()
        const ringCenterX = rect.left + rect.width / 2
        const ringCenterY = rect.top + rect.height / 2

        const deltaX = (e.clientX - ringCenterX) * 0.012
        const deltaY = (e.clientY - ringCenterY) * 0.012

        setRings(prev => prev.map(r =>
          r.id === id ? { ...r, translateX: deltaX, translateY: deltaY } : r
        ))
      })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [rings])

  useEffect(() => {
    const timer = setInterval(() => {
      setRings(prevRings => {
        const currentCount = prevRings.filter(r => !r.removing).length
        const random = Math.random()

        if (random < 0.3 && currentCount > MIN_RINGS) {
          const visibleRings = prevRings.filter(r => !r.removing)
          const indexToRemove = Math.floor(Math.random() * visibleRings.length)
          const idToRemove = visibleRings[indexToRemove].id
          return prevRings.map(r => r.id === idToRemove ? { ...r, removing: true } : r)
        } else if (random > 0.7 && currentCount < MAX_RINGS) {
          const newRing = createRing(prevRings)
          return [...prevRings, newRing]
        }
        return prevRings
      })
    }, 3000)

    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const cleanupTimer = setInterval(() => {
      setRings(prev => {
        const toRemove = prev.filter(r => r.removing && r.opacity === 0)
        toRemove.forEach(r => ringsRef.current.delete(r.id))
        return prev.filter(r => !(r.removing && r.opacity === 0))
      })

      setRings(prev => prev.map(r => {
        if (r.appearing && r.opacity < 1) {
          return { ...r, opacity: Math.min(1, r.opacity + 0.05) }
        }
        if (r.appearing && r.opacity >= 1) {
          return { ...r, opacity: 1, appearing: false }
        }
        if (r.removing && r.opacity > 0) {
          return { ...r, opacity: Math.max(0, r.opacity - 0.05) }
        }
        return r
      }))
    }, 50)

    return () => clearInterval(cleanupTimer)
  }, [])

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
        overflow: 'hidden'
      }}
    >
      {rings.map((ring) => (
        <div
          key={ring.id}
          ref={(el) => {
            if (el) ringsRef.current.set(ring.id, el)
            else ringsRef.current.delete(ring.id)
          }}
          style={{
            position: 'absolute',
            left: `${ring.x}%`,
            top: `${ring.y}%`,
            width: `${ring.size}px`,
            height: `${ring.size}px`,
            borderRadius: '50%',
            border: `${ring.borderWidth}px solid ${ring.borderColor}`,
            willChange: 'transform, opacity',
          }}
        />
      ))}
    </div>
  )
}

export default BackgroundDecoration
