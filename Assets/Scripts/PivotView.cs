using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PivotView : MonoBehaviour
{
    [Range(45, 60)]
    public int angle;
    public Transform customPivot;

    private void Awake()
    {
        transform.RotateAround(customPivot.position, Vector3.up, RotateView(angle, 45, 60, 0, -15));
    }

    private int RotateView(int angle, int inputStart, int inputEnd, int outputStart, int outputEnd)
    {
        return outputStart + ((outputEnd - outputStart) / (inputEnd - inputStart)) * (angle - inputStart);
    }
}
