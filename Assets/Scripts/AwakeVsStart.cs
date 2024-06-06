using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AwakeVsStart : MonoBehaviour
{
    public void Awake()
    {
        Debug.Log("Awake got called");
    }

    private void Start()
    {
        Debug.Log("Start got called");
    }


}
